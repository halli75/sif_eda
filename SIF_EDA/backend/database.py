"""
Database connection utilities for FastAPI.

This module initialises an async SQLAlchemy engine and provides a session
dependency for FastAPI routes. The database URL is read from the
environment variable `DATABASE_URL`. You can set this in a `.env` file
and load it using `python-dotenv` or by exporting it before running
uvicorn.
"""
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Retrieve database URL from environment or fallback to a sensible default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/polymarket")

# Create a single engine instance for the application
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Session maker for dependency injection
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncSession:
    """
    FastAPI dependency that yields an async session and ensures it is
    properly closed after the request.
    """
    async with AsyncSessionLocal() as session:
        yield session