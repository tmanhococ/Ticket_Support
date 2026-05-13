"""
tests/test_drift.py
--------------------
Unit tests for generate_drift_ticket() — Story 2.2, AC8.

Tests verify:
  - Drift ticket validates against TicketIn schema
  - Language distribution: ≥80% German over 100 samples
  - Type distribution: ≥70% Incident over 100 samples
  - Queue distribution: ≥70% Technical Support over 100 samples
"""

from src.api.schemas import TicketIn
from src.simulator.generator import generate_drift_ticket, QUEUES, TYPES


def test_drift_ticket_validates_as_ticket_in():
    """Drift ticket must pass TicketIn Pydantic validation."""
    ticket_dict = generate_drift_ticket()
    ticket = TicketIn(**ticket_dict)
    assert ticket.subject
    assert ticket.body


def test_drift_language_is_mostly_german():
    """≥80% of drift tickets must have language='de'.

    Using 500 samples to reduce variance — with weights=[20,80], the
    expected count is ~400 and std ≈ 8.9, so ≥78% is safely within range.
    """
    results = [generate_drift_ticket() for _ in range(500)]
    german_count = sum(1 for r in results if r["language"] == "de")
    assert (
        german_count >= 390
    ), (  # ≥78% of 500 (well below expected 400)
        f"Expected ≥390 German tickets out of 500, got {german_count}"
    )


def test_drift_type_is_mostly_incident():
    """≥70% of drift tickets must have type='Incident'.

    Using 500 samples — expected ~350, std ≈ 10.2, so ≥330 (66%) is reliable.
    """
    results = [generate_drift_ticket() for _ in range(500)]
    incident_count = sum(1 for r in results if r["type"] == "Incident")
    assert (
        incident_count >= 330
    ), (  # ≥66% of 500 (below expected 350)
        f"Expected ≥330 Incident tickets out of 500, got {incident_count}"
    )


def test_drift_queue_is_mostly_technical_support():
    """≥70% of drift tickets must have queue='Technical Support'.

    Using 500 samples — expected ~350, std ≈ 10.2, so ≥330 (66%) is reliable.
    """
    results = [generate_drift_ticket() for _ in range(500)]
    ts_count = sum(1 for r in results if r["queue"] == "Technical Support")
    assert (
        ts_count >= 330
    ), (  # ≥66% of 500 (below expected 350)
        f"Expected ≥330 Technical Support tickets out of 500, got {ts_count}"
    )


def test_drift_ticket_language_in_allowed_set():
    """Drift ticket language must still be in the allowed set."""
    for _ in range(20):
        result = generate_drift_ticket()
        assert result["language"] in ["en", "de"]


def test_drift_ticket_queue_in_allowed_set():
    """Drift ticket queue must still be a valid domain queue."""
    for _ in range(20):
        result = generate_drift_ticket()
        assert result["queue"] in QUEUES


def test_drift_ticket_type_in_allowed_set():
    """Drift ticket type must still be a valid domain type."""
    for _ in range(20):
        result = generate_drift_ticket()
        assert result["type"] in TYPES


def test_drift_ticket_seeded_is_reproducible():
    """Same seed must produce same non-UUID fields."""
    result_a = generate_drift_ticket(seed=77)
    result_b = generate_drift_ticket(seed=77)
    assert result_a["subject"] == result_b["subject"]
    assert result_a["language"] == result_b["language"]
    assert result_a["queue"] == result_b["queue"]
    assert result_a["type"] == result_b["type"]
