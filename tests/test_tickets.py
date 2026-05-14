"""
Integration tests for POST /tickets/ endpoint.

ACs covered:
  AC1 — Valid POST returns 201 with ticket_id and timestamp.
  AC2 — Invalid payload returns 422 (Pydantic, automatic).
  AC4 — DB write failure returns 503 with detail="storage_unavailable".
  AC5 — /health still returns 200 (regression guard).
  AC6 — All three scenarios tested with mocked DB session.

Pattern: FastAPI dependency_overrides (correct approach for async deps).
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.api.database import get_db
from src.api.main import app

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

VALID_TICKET: dict = {
    "ticket_id": str(uuid4()),
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "subject": "Cannot login to portal",
    "body": "Users report login failures since the last deployment at 14:00 UTC.",
    "language": "en",
    "queue": "Technical Support",
    "type": "Incident",
}


# ---------------------------------------------------------------------------
# Dependency override helpers
# ---------------------------------------------------------------------------


def _make_ok_session() -> AsyncMock:
    """Async DB session that succeeds on commit."""
    session = AsyncMock()
    session.add = MagicMock()  # synchronous add
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


def _make_fail_session() -> AsyncMock:
    """Async DB session that raises SQLAlchemyError on commit."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock(side_effect=SQLAlchemyError("connection lost"))
    session.rollback = AsyncMock()
    return session


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_ticket_returns_201(client):
    """AC1: Valid ticket → 201 with ticket_id and timestamp in body."""
    mock_session = _make_ok_session()

    async def override():
        yield mock_session

    app.dependency_overrides[get_db] = override
    try:
        response = await client.post("/tickets/", json=VALID_TICKET)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert "ticket_id" in body
    assert "timestamp" in body
    assert body["ticket_id"] == VALID_TICKET["ticket_id"]


@pytest.mark.asyncio
async def test_create_ticket_returns_201_minimal_payload(client):
    """AC1: Minimal valid ticket (only required fields) → 201."""
    minimal = {
        "ticket_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subject": "Server is down",
        "body": "Production server not responding.",
    }
    mock_session = _make_ok_session()

    async def override():
        yield mock_session

    app.dependency_overrides[get_db] = override
    try:
        response = await client.post("/tickets/", json=minimal)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_invalid_payload_missing_subject_returns_422(client):
    """AC2: Missing 'subject' field → 422 (Pydantic, no DB interaction)."""
    invalid = {k: v for k, v in VALID_TICKET.items() if k != "subject"}
    response = await client.post("/tickets/", json=invalid)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_payload_empty_body_returns_422(client):
    """AC2: Empty 'body' field → 422."""
    invalid = {**VALID_TICKET, "body": ""}
    response = await client.post("/tickets/", json=invalid)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_payload_bad_uuid_returns_422(client):
    """AC2: Non-UUID ticket_id → 422."""
    invalid = {**VALID_TICKET, "ticket_id": "not-a-uuid"}
    response = await client.post("/tickets/", json=invalid)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_db_write_failure_returns_503(client):
    """AC4: SQLAlchemyError on commit → 503 with detail='storage_unavailable'."""
    mock_session = _make_fail_session()

    async def override():
        yield mock_session

    app.dependency_overrides[get_db] = override
    try:
        response = await client.post("/tickets/", json=VALID_TICKET)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["detail"] == "storage_unavailable"
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_health_still_returns_200_after_tickets_route_added(client):
    """AC5: /health regression guard — still 200 after tickets router registered."""
    from unittest.mock import patch

    with patch(
        "src.api.routes.health.check_db_connection",
        new_callable=AsyncMock,
        return_value=True,
    ):
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_ticket_shadow_inference_success(client):
    """Test that predicted_priority is assigned when model inference succeeds."""
    mock_session = _make_ok_session()

    # Mock model service on app state
    mock_model_service = MagicMock()
    mock_model_service.model = MagicMock()
    mock_model_service.predict.return_value = ["high"]
    app.state.model_service = mock_model_service

    async def override():
        yield mock_session

    app.dependency_overrides[get_db] = override
    try:
        response = await client.post("/tickets/", json=VALID_TICKET)
    finally:
        app.dependency_overrides.clear()
        # Clean up app state
        delattr(app.state, "model_service")

    assert response.status_code == 201
    mock_model_service.predict.assert_called_once_with(
        [f"{VALID_TICKET['subject']} {VALID_TICKET['body']}"]
    )
    # Verify it was added to session with predicted_priority
    added_ticket = mock_session.add.call_args[0][0]
    assert added_ticket.predicted_priority == "high"


@pytest.mark.asyncio
async def test_create_ticket_shadow_inference_failure_graceful(client):
    """Test that the API still returns 201 when model inference fails."""
    mock_session = _make_ok_session()

    mock_model_service = MagicMock()
    mock_model_service.model = MagicMock()
    mock_model_service.predict.side_effect = Exception("Model exploded")
    app.state.model_service = mock_model_service

    async def override():
        yield mock_session

    app.dependency_overrides[get_db] = override
    try:
        response = await client.post("/tickets/", json=VALID_TICKET)
    finally:
        app.dependency_overrides.clear()
        delattr(app.state, "model_service")

    assert response.status_code == 201
    mock_model_service.predict.assert_called_once()
    added_ticket = mock_session.add.call_args[0][0]
    # Priority should not be set
    assert getattr(added_ticket, "predicted_priority", None) is None
