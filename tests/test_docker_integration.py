"""
Docker integration smoke tests — Story 3.1

These tests verify that the running Docker containers are healthy and
the API is reachable. They are SKIPPED by default to prevent breaking
normal unit test runs when Docker is not running.

To run:
    DOCKER_INTEGRATION=1 pytest tests/test_docker_integration.py -v
"""

import os

import httpx
import pytest

DOCKER_INTEGRATION = os.environ.get("DOCKER_INTEGRATION", "0") == "1"
skip_reason = "Docker integration tests skipped (set DOCKER_INTEGRATION=1 to enable)"


@pytest.mark.skipif(not DOCKER_INTEGRATION, reason=skip_reason)
def test_api_health_endpoint_reachable():
    """Smoke test: API container is running and /health returns 200."""
    response = httpx.get("http://localhost:8000/health", timeout=10.0)
    assert response.status_code == 200, f"Expected 200 from /health, got {response.status_code}"


@pytest.mark.skipif(not DOCKER_INTEGRATION, reason=skip_reason)
def test_api_health_returns_ok_status():
    """API /health endpoint should report status: ok."""
    response = httpx.get("http://localhost:8000/health", timeout=10.0)
    body = response.json()
    assert "status" in body, f"Expected 'status' key in /health response, got: {body}"
    assert body["status"] == "ok", f"Expected status='ok', got: {body['status']}"


@pytest.mark.skipif(not DOCKER_INTEGRATION, reason=skip_reason)
def test_api_tickets_endpoint_accepts_valid_payload():
    """Verify the /tickets/ endpoint is reachable and accepts a valid ticket."""
    import uuid
    from datetime import datetime, timezone

    payload = {
        "ticket_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subject": "Docker integration test ticket",
        "body": "This ticket was sent during a Docker smoke test.",
        "language": "en",
        "queue": "General Inquiry",
        "type": "Request",
    }
    response = httpx.post("http://localhost:8000/tickets/", json=payload, timeout=10.0)
    assert (
        response.status_code == 201
    ), f"Expected 201 Created, got {response.status_code}: {response.text}"
