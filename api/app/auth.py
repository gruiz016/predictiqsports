# api/app/auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
import jwt, uuid
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .config import settings
from .db import SessionLocal
from .models import User, Subscription

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password:str)->str: return pwd_context.hash(password)
def verify_password(plain:str, hashed:str)->bool: return pwd_context.verify(plain, hashed)
def create_jwt(user_id:str, email:str)->str:
    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload={"sub":user_id,"email":email,"exp":exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

async def get_db():
    async with SessionLocal() as session:
        yield session

async def require_auth(authorization: Optional[str]=Header(default=None), db: AsyncSession=Depends(get_db)):
    if settings.DEV_SKIP_AUTH:
        class U: pass
        u=U(); u.id="dev-user"; u.email="dev@local"
        return {"user":u, "sub_active":True}
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    token=authorization.split(" ",1)[1].strip()
    try:
        payload=jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id_str=payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    try:
        user_id=uuid.UUID(user_id_str)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user id in token")
    user=(await db.execute(select(User).where(User.id==user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    sub=(await db.execute(select(Subscription).where(Subscription.user_id==user_id))).scalar_one_or_none()
    sub_active=bool(sub and sub.status=="active" and (sub.current_period_end is None or sub.current_period_end>datetime.now(tz=timezone.utc)))
    return {"user":user, "sub_active":sub_active}
