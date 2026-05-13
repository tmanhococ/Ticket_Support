"""
tests/test_generator.py
-----------------------
Unit tests for src/simulator/generator.py — Story 2.1

Tests cover:
  - Valid ticket generation (AC1–AC7)
  - Invalid ticket generation / corruption patterns (AC8)
"""

import uuid

import pytest
from pydantic import ValidationError

from src.api.schemas import TicketIn
from src.simulator.generator import (
    INVALID_PATTERNS,
    QUEUES,
    TYPES,
    generate_invalid_ticket,
    generate_ticket,
)

# ===========================================================================
# Valid ticket tests (AC1 – AC7)
# ===========================================================================


def test_output_validates_as_ticket_in():
    """Generated dict must pass TicketIn Pydantic validation (AC1)."""
    ticket_dict = generate_ticket()
    ticket = TicketIn(**ticket_dict)
    assert ticket.subject  # non-empty
    assert ticket.body  # non-empty


def test_ticket_id_is_valid_uuid_v4():
    """ticket_id must be a valid UUID v4 string (AC1)."""
    result = generate_ticket()
    parsed = uuid.UUID(result["ticket_id"])  # raises ValueError if invalid
    assert parsed.version == 4


def test_language_in_allowed_set():
    """language must be 'en' or 'de' (AC3)."""
    for _ in range(30):
        result = generate_ticket()
        assert result["language"] in ["en", "de"], f"Unexpected language: {result['language']!r}"


def test_queue_in_allowed_set():
    """queue must be one of the defined domain queues (AC4)."""
    for _ in range(30):
        result = generate_ticket()
        assert result["queue"] in QUEUES, f"Unexpected queue: {result['queue']!r}"


def test_type_in_allowed_set():
    """type must be one of the defined ticket types (AC5)."""
    for _ in range(30):
        result = generate_ticket()
        assert result["type"] in TYPES, f"Unexpected type: {result['type']!r}"


def test_seeded_output_is_reproducible():
    """Same seed must produce same non-UUID fields (AC6)."""
    result_a = generate_ticket(seed=42)
    result_b = generate_ticket(seed=42)
    # ticket_id uses uuid4() (OS-random) — exclude from comparison
    assert result_a["subject"] == result_b["subject"]
    assert result_a["body"] == result_b["body"]
    assert result_a["language"] == result_b["language"]
    assert result_a["queue"] == result_b["queue"]
    assert result_a["type"] == result_b["type"]


def test_consecutive_calls_produce_unique_ticket_ids():
    """Consecutive calls must return different ticket_ids (AC1)."""
    result_a = generate_ticket()
    result_b = generate_ticket()
    assert result_a["ticket_id"] != result_b["ticket_id"]


def test_subject_and_body_are_non_empty_strings():
    """Subject and body must be non-empty strings (AC2)."""
    for _ in range(20):
        result = generate_ticket()
        assert isinstance(result["subject"], str) and result["subject"].strip()
        assert isinstance(result["body"], str) and result["body"].strip()


def test_required_fields_all_present():
    """All required TicketIn fields must exist in returned dict (AC1)."""
    result = generate_ticket()
    for field in ("ticket_id", "timestamp", "subject", "body"):
        assert field in result, f"Missing required field: {field!r}"


# ===========================================================================
# Invalid ticket tests (AC8)
# ===========================================================================


def test_invalid_ticket_always_fails_validation():
    """Random invalid ticket must ALWAYS raise ValidationError (AC8)."""
    for _ in range(30):
        bad_dict = generate_invalid_ticket()
        with pytest.raises(ValidationError):
            TicketIn(**bad_dict)


@pytest.mark.parametrize("pattern", INVALID_PATTERNS)
def test_each_corruption_pattern_fails_validation(pattern: str):
    """Every specific corruption pattern must cause ValidationError (AC8)."""
    bad_dict = generate_invalid_ticket(pattern=pattern)
    with pytest.raises(ValidationError):
        TicketIn(**bad_dict)


def test_invalid_ticket_with_unknown_pattern_raises_value_error():
    """Passing an unknown pattern name must raise ValueError (guard-rail)."""
    with pytest.raises(ValueError, match="Unknown invalid pattern"):
        generate_invalid_ticket(pattern="nonexistent_pattern")


def test_invalid_ticket_seeded_is_reproducible():
    """Same seed must select the same corruption pattern (AC6 extended)."""
    result_a = generate_invalid_ticket(seed=99)
    result_b = generate_invalid_ticket(seed=99)
    # Both should have the same keys present/absent (same pattern was applied)
    assert set(result_a.keys()) == set(result_b.keys())
