"""
Health-check endpoint.

GET /health → {"status": "ok", "db": "connected" | "unavailable"}

Always returns HTTP 200 — never 500 — even when DB is down.
"""
from fastapi import APIRouter

from src.api.database import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health", summary="Service liveness and DB connectivity probe")
async def health_check() -> dict:
    """
    Returns service status and DB reachability.

    - status: always "ok" (service is alive)
    - db: "connected" if PostgreSQL is reachable, "unavailable" otherwise
    """
    db_ok = await check_db_connection()
    return {
        "status": "ok",
        "db": "connected" if db_ok else "unavailable",
    }
