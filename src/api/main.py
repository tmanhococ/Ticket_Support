"""
FastAPI application entrypoint — Ticket Triage MLOps.

Architecture rules (architecture.md §2.1, §5):
- Async-first: all routes are async def.
- PostgreSQL via asyncpg from Day 1.
- No Celery, Kafka, or Airflow.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.database import create_tables, engine
from src.api.routes import health, tickets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage DB engine lifecycle."""
    logger.info("Starting Ticket Triage API — connecting to DB...")
    try:
        await create_tables()
        logger.info("DB tables ensured / connection pool initialised.")
    except Exception as exc:  # noqa: BLE001
        # Graceful degradation: log but do NOT crash on startup
        logger.warning("DB unavailable at startup (will retry per-request): %s", exc)
    yield
    logger.info("Shutting down — disposing DB connection pool...")
    await engine.dispose()


app = FastAPI(
    title="Ticket Triage MLOps API",
    version="0.1.0",
    description="Intake and inference API for MLOps ticket triage system.",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(tickets.router)
