# api/app/routers_auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .auth import get_db, hash_password, verify_password, create_jwt
from .models import User
from .schemas import RegisterRequest, LoginRequest, LoginResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/v1/auth", tags=["auth"])

@router.post("/register", response_model=LoginResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    email = body.email.lower()
    existing = (await db.execute(select(User).where(User.email==email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(email=email, created_at=datetime.now(tz=timezone.utc), password_hash=hash_password(body.password))
    db.add(user)
    await db.flush()  # get server/default PK value
    token=create_jwt(str(user.id), user.email)
    await db.commit()
    return LoginResponse(token=token, user_id=str(user.id), email=user.email)

@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    email=body.email.lower()
    user=(await db.execute(select(User).where(User.email==email))).scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token=create_jwt(str(user.id), user.email)
    return LoginResponse(token=token, user_id=str(user.id), email=user.email)
