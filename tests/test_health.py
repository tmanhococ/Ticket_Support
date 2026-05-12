"""
Tests for GET /health endpoint.

ACs covered:
  AC1 — /health returns HTTP 200 with correct JSON body.
  AC4 — DB unavailability never causes HTTP 500 (graceful degradation).
"""
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_health_returns_200_when_db_connected(client):
    """AC1: /health → 200 {"status": "ok", "db": "connected"} when DB is up."""
    with patch(
        "src.api.routes.health.check_db_connection",
        new_callable=AsyncMock,
        return_value=True,
    ):
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["db"] == "connected"


@pytest.mark.asyncio
async def test_health_returns_200_when_db_unavailable(client):
    """
    AC4 — Graceful degradation: DB down must NOT cause HTTP 500.
    /health still returns 200 with db='unavailable'.
    """
    with patch(
        "src.api.routes.health.check_db_connection",
        new_callable=AsyncMock,
        return_value=False,
    ):
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["db"] == "unavailable"


@pytest.mark.asyncio
async def test_health_response_schema(client):
    """Health response always has exactly 'status' and 'db' keys."""
    with patch(
        "src.api.routes.health.check_db_connection",
        new_callable=AsyncMock,
        return_value=True,
    ):
        response = await client.get("/health")

    body = response.json()
    assert set(body.keys()) == {"status", "db"}
