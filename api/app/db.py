# api/app/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from .config import settings
engine=create_async_engine(settings.DATABASE_URL, echo=False, future=True)
SessionLocal=async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
async def healthcheck()->bool:
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    return True
