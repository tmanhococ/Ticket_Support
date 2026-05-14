"""
src/drift_monitor/db_reader.py
--------------------------------
Synchronous database reader for the Drift Monitor.

Uses psycopg2-based SQLAlchemy (sync) — the drift monitor runs as a
standalone script/container, not under FastAPI's async event loop.

Design rules (architecture.md §4):
- Never crash on DB unavailability; raise DriftMonitorError with clear message.
- Return pandas DataFrames ready for EvidentlyAI.
"""

import logging
from datetime import datetime, timedelta, timezone

import pandas as pd
from sqlalchemy import create_engine, text

from src.drift_monitor.config import (
    CURRENT_WINDOW_HOURS,
    DATABASE_URL,
    REFERENCE_SAMPLE_SIZE,
)

logger = logging.getLogger(__name__)


class DriftMonitorError(Exception):
    """Raised when the drift monitor cannot proceed due to data issues."""


def _get_engine():
    """Return a synchronous SQLAlchemy engine."""
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def fetch_reference_data(
    engine=None,
    sample_size: int = REFERENCE_SAMPLE_SIZE,
) -> pd.DataFrame:
    """
    Fetch the oldest N tickets as the reference (baseline) dataset.

    Args:
        engine: Optional SQLAlchemy engine (injected for testing).
        sample_size: Number of tickets to fetch as baseline.

    Returns:
        DataFrame with columns: ticket_id, subject, body, language, queue,
        type, predicted_priority, received_at.

    Raises:
        DriftMonitorError: If not enough data is available.
    """
    if engine is None:
        engine = _get_engine()

    query = text(
        """
        SELECT ticket_id, subject, body, language, queue, type,
               predicted_priority, received_at
        FROM tickets
        ORDER BY received_at ASC
        LIMIT :limit
        """
    )
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"limit": sample_size})
    except Exception as exc:
        raise DriftMonitorError(f"Failed to fetch reference data: {exc}") from exc

    if df.empty:
        raise DriftMonitorError("Reference dataset is empty — need at least 1 ticket.")

    logger.info("Fetched %d reference tickets.", len(df))
    return df


def fetch_current_data(
    engine=None,
    window_hours: int = CURRENT_WINDOW_HOURS,
) -> pd.DataFrame:
    """
    Fetch tickets received within the last `window_hours` hours.

    Args:
        engine: Optional SQLAlchemy engine (injected for testing).
        window_hours: Look-back window in hours.

    Returns:
        DataFrame with same columns as fetch_reference_data.

    Raises:
        DriftMonitorError: If no current data is available.
    """
    if engine is None:
        engine = _get_engine()

    cutoff: datetime = datetime.now(tz=timezone.utc) - timedelta(hours=window_hours)

    query = text(
        """
        SELECT ticket_id, subject, body, language, queue, type,
               predicted_priority, received_at
        FROM tickets
        WHERE received_at >= :cutoff
        ORDER BY received_at DESC
        """
    )
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"cutoff": cutoff})
    except Exception as exc:
        raise DriftMonitorError(f"Failed to fetch current data: {exc}") from exc

    if df.empty:
        raise DriftMonitorError(f"No current data found in the last {window_hours} hours.")

    logger.info("Fetched %d current tickets (last %dh).", len(df), window_hours)
    return df
