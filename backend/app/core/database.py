from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy models."""


engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,  # validate connections before use
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session():
    """FastAPI dependency that yields an async DB session per request."""
    async with AsyncSessionLocal() as session:
        yield session
