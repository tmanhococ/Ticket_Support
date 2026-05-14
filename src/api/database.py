"""
Database connection module — async SQLAlchemy engine with asyncpg driver.

Design rules (08_agent_workflow_rules.md §3):
- Never crash on DB unavailability; log warning and degrade gracefully.
- Use async engine (postgresql+asyncpg://) — NOT synchronous psycopg2.
"""

import logging
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://tickets_user:tickets_pass@db:5432/tickets_db",
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # verifies connections before use
    pool_size=20,
    max_overflow=10,
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db():
    """FastAPI dependency — yields an async DB session."""
    async with AsyncSessionLocal() as session:
        yield session


async def check_db_connection() -> bool:
    """
    Probe the DB with a lightweight query.

    Returns True if reachable, False otherwise.
    NEVER raises — graceful degradation is mandatory.
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("DB connection check failed: %s", exc)
        return False


async def create_tables() -> None:
    """
    Create all ORM-defined tables if they do not exist.

    Uses `checkfirst=True` implicitly via create_all — safe to call on every startup.
    Import is deferred inside function to avoid circular import at module level.
    """
    from src.api.models import Base  # noqa: PLC0415 — intentional deferred import

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
