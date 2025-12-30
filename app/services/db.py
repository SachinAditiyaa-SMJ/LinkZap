import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

# Database configuration
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "linkzap")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pass")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{
    POSTGRES_HOST
}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"

engine: AsyncEngine | None = None

# Create declarative base
Base = declarative_base()


async def init_db_engine():
    global engine
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before using
        echo=False,
    )


async def create_tables():
    if engine is None:
        raise RuntimeError("Engine not initialized")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Sync call in async ctx


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if not engine:
        raise RuntimeError("Database engine not initialised")
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    async with async_session() as session:
        yield session
