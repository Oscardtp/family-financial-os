from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from fastapi import HTTPException
from app.config import get_settings

settings = get_settings()

connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}

if "postgresql" in settings.DATABASE_URL:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=1800,
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args=connect_args,
    )
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
        except HTTPException:
            await session.rollback()
            raise
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
