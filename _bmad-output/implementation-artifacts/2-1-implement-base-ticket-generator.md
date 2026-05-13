# Story 2.1: Implement Base Ticket Generator

Status: review

## Story

As a Developer,
I want a script that generates both valid and intentionally invalid support tickets,
So that I can test the system's data ingestion pipeline — verifying valid tickets are saved and invalid tickets are rejected before reaching the database.

## Acceptance Criteria

1. **[AC1]** A `generate_ticket()` function in `src/simulator/generator.py` returns a Python `dict` matching the `TicketIn` Pydantic schema: `ticket_id` (UUID v4), `subject` (str, non-empty), `body` (str, non-empty), `timestamp` (ISO8601 with timezone), plus optional `language`, `queue`, `type`.
2. **[AC2]** Generated `subject` and `body` content looks like a realistic IT support ticket — not generic Lorem Ipsum. Text is drawn from a curated pool of templates matching real domain vocabulary (Technical Support, Billing, Incidents, etc.).
3. **[AC3]** Generated `language` is randomly sampled from `["en", "de"]` (matching the real dataset distribution). English templates dominate (~70%), German templates exist (~30%).
4. **[AC4]** Generated `queue` is randomly sampled from the defined domain queues: `Technical Support`, `Customer Service`, `Billing and Payments`, `Product Support`, `IT Support`.
5. **[AC5]** Generated `type` is randomly sampled from: `Incident`, `Request`, `Problem`, `Change`.
6. **[AC6]** The function is fully deterministic when seeded — `random.seed(42)` produces the same output every time (enables reproducible testing).
7. **[AC7]** Unit tests verify: output matches the `TicketIn` schema (Pydantic validation passes), `ticket_id` is always a unique UUID, `language` is always in `["en", "de"]`, `queue` and `type` are always in their allowed sets, seeded output is reproducible.
8. **[AC8]** A `generate_invalid_ticket()` function returns a `dict` that **intentionally fails** `TicketIn` Pydantic validation. The function randomly selects one of the following corruption patterns:
   - **missing_required_field**: omits `subject`, `body`, `ticket_id`, or `timestamp` entirely
   - **empty_subject**: `subject = ""`
   - **empty_body**: `body = ""`
   - **invalid_uuid**: `ticket_id = "not-a-uuid-at-all"`
   - **malformed_timestamp**: `timestamp = "2024-13-99T99:99:99"` (unparseable)
   
   Unit tests verify that `TicketIn(**generate_invalid_ticket())` always raises `ValidationError`.

## Tasks / Subtasks

- [x] Task 1: Create `src/simulator/generator.py` with `generate_ticket()` function (AC: #1, #2, #3, #4, #5, #6)
  - [x] 1.1 Define English ticket template pools: `SUBJECTS_EN` (list of 10+ realistic subject strings), `BODIES_EN` (list of 10+ realistic body strings matching corresponding subjects)
  - [x] 1.2 Define German ticket template pools: `SUBJECTS_DE` (list of 5+ realistic German subject strings from `data_info.md` examples), `BODIES_DE` (list of 5+ realistic German body strings)
  - [x] 1.3 Define `QUEUES` list and `TYPES` list from the domain values
  - [x] 1.4 Implement `generate_ticket(seed: int | None = None) -> dict` — call `random.seed(seed)` when seed provided, then sample all fields
  - [x] 1.5 Use `uuid.uuid4()` for `ticket_id`, `datetime.now(timezone.utc).isoformat()` for `timestamp`
  - [x] 1.6 Language sampling: 70% English, 30% German — use `random.choices(["en", "de"], weights=[70, 30])`
  - [x] 1.7 Match English subject with English body (same index from pool), German with German
- [x] Task 2: Ensure `src/simulator/__init__.py` exists (AC: #1)
  - [x] 2.1 Create `src/simulator/__init__.py` if not already present (may be empty)
- [x] Task 3: Write unit tests in `tests/test_generator.py` (AC: #7)
  - [x] 3.1 Test output is a valid `TicketIn` — import `TicketIn` from `src.api.schemas` and call `TicketIn(**generate_ticket())` — must not raise
  - [x] 3.2 Test `ticket_id` is a valid UUID string (no exceptions on `UUID(result["ticket_id"])`)
  - [x] 3.3 Test `language` in `["en", "de"]`
  - [x] 3.4 Test `queue` in allowed set
  - [x] 3.5 Test `type` in allowed set
  - [x] 3.6 Test seeded reproducibility: `generate_ticket(seed=42) == generate_ticket(seed=42)`
  - [x] 3.7 Test uniqueness: two consecutive unseeded calls produce different `ticket_id`s
- [x] Task 4: Add `generate_invalid_ticket()` to `src/simulator/generator.py` (AC: #8)
  - [x] 4.1 Define `INVALID_PATTERNS` list: `["missing_subject", "missing_body", "missing_ticket_id", "missing_timestamp", "empty_subject", "empty_body", "invalid_uuid", "malformed_timestamp"]`
  - [x] 4.2 Implement `generate_invalid_ticket(seed: int | None = None) -> dict` — start from a valid base ticket dict, then apply one randomly chosen corruption pattern
  - [x] 4.3 Corruption logic:
    - `missing_subject` / `missing_body` / `missing_ticket_id` / `missing_timestamp` → `del ticket[field]`
    - `empty_subject` → `ticket["subject"] = ""`
    - `empty_body` → `ticket["body"] = ""`
    - `invalid_uuid` → `ticket["ticket_id"] = "not-a-valid-uuid"`
    - `malformed_timestamp` → `ticket["timestamp"] = "2024-13-99T99:99:99"`
- [x] Task 5: Add invalid ticket tests to `tests/test_generator.py` (AC: #8)
  - [x] 5.1 Test `generate_invalid_ticket()` always raises `ValidationError` when passed to `TicketIn(**...)`
  - [x] 5.2 Test all 8 corruption patterns individually — each must raise `ValidationError`
  - [x] 5.3 Test that `generate_ticket()` and `generate_invalid_ticket()` remain independent (generating one does not affect seeding of the other)
- [x] Task 6: Verify no regressions in existing tests (AC: all)
  - [x] 6.1 Run `pytest tests/` — all 47 tests pass (27 existing + 20 new)

## Dev Notes

### Previous Story Intelligence
**Epic 1 — Established patterns (MUST reuse, do NOT reinvent):**
- `TicketIn` schema is defined in `src/api/schemas.py` — import from there. The schema accepts: `ticket_id` (UUID), `timestamp` (datetime), `subject` (str, non-empty), `body` (str, non-empty), `language` (Optional[str]), `queue` (Optional[str]), `type` (Optional[str]).
- `str_strip_whitespace=True` is already set on `TicketIn` — whitespace-only strings will fail validation. Generated text must have real content.
- Import path convention: `from src.api.schemas import TicketIn` (used consistently throughout the codebase).
- Test infrastructure: `pytest.ini` sets `asyncio_mode = auto`, `tests/conftest.py` defines the `client` fixture. This story's tests are **synchronous** (no async), they will still run correctly.

### Generator Implementation Pattern
```python
# src/simulator/generator.py
import random
import uuid
from datetime import datetime, timezone
from typing import Optional

# --- English Template Pool ---
SUBJECTS_EN = [
    "Cannot login to the portal",
    "Account locked after multiple failed attempts",
    "Payment not processed correctly",
    "System outage affecting all users",
    "Data not syncing between devices",
    "Feature request: export to CSV",
    "Performance degradation on dashboard",
    "Security alert: unauthorized access attempt",
    "Invoice shows incorrect amount",
    "Product returns process unclear",
]

BODIES_EN = [
    "Users are unable to log in to the main portal since the last deployment. The login button becomes unresponsive after entering credentials.",
    "Our account has been locked after three failed login attempts. We need immediate access restored for the operations team.",
    "A payment of $500 was debited from our account but the system shows the order as 'Payment Pending'. Please investigate.",
    "The entire system appears to be offline for the past 30 minutes. All employees are affected and business operations have halted.",
    "Data entered on mobile devices is not appearing on the desktop application. This inconsistency is causing issues for our field team.",
    "We would like the ability to export all ticket data to CSV format for our weekly reporting. Please consider adding this feature.",
    "The analytics dashboard has become very slow to load over the past week, taking more than 2 minutes to display data.",
    "We detected an unauthorized login attempt from an unknown IP address. Please review and secure our account immediately.",
    "Our latest invoice (#INV-2024-0531) shows a charge for a service we cancelled in March. Please issue a corrected invoice.",
    "We need to return 3 items from order #ORD-9876 but the returns portal keeps showing an error when we submit the request.",
]

# --- German Template Pool ---
SUBJECTS_DE = [
    "Wesentlicher Sicherheitsvorfall",
    "Anmeldeproblem seit dem letzten Update",
    "Rechnungsfehler für Monat Mai",
    "System reagiert nicht mehr",
    "Frage zur Produktkompatibilität",
]

BODIES_DE = [
    "Sehr geehrtes Support-Team, ich möchte einen gravierenden Sicherheitsvorfall melden, der mehrere Komponenten unserer Infrastruktur betrifft. Bitte reagieren Sie umgehend.",
    "Seit dem letzten Software-Update können sich mehrere Mitarbeiter nicht mehr in das System einloggen. Bitte prüfen Sie das Problem.",
    "Unsere Rechnung vom Mai enthält Posten für Dienste, die wir bereits im April storniert haben. Bitte korrigieren Sie dies.",
    "Das gesamte System reagiert seit etwa einer Stunde nicht mehr auf Anfragen. Alle unsere Mitarbeiter sind davon betroffen.",
    "Ich benötige Informationen zur Kompatibilität Ihrer Produkte mit unserem bestehenden ERP-System. Bitte senden Sie Details.",
]

QUEUES = [
    "Technical Support",
    "Customer Service",
    "Billing and Payments",
    "Product Support",
    "IT Support",
]

TYPES = ["Incident", "Request", "Problem", "Change"]

INVALID_PATTERNS = [
    "missing_subject",
    "missing_body",
    "missing_ticket_id",
    "missing_timestamp",
    "empty_subject",
    "empty_body",
    "invalid_uuid",
    "malformed_timestamp",
]


def _build_base_ticket() -> dict:
    """Internal helper — builds a valid ticket dict (not seeded)."""
    language = random.choices(["en", "de"], weights=[70, 30])[0]
    if language == "en":
        idx = random.randrange(len(SUBJECTS_EN))
        subject, body = SUBJECTS_EN[idx], BODIES_EN[idx]
    else:
        idx = random.randrange(len(SUBJECTS_DE))
        subject, body = SUBJECTS_DE[idx], BODIES_DE[idx]
    return {
        "ticket_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subject": subject,
        "body": body,
        "language": language,
        "queue": random.choice(QUEUES),
        "type": random.choice(TYPES),
    }


def generate_ticket(seed: int | None = None) -> dict:
    """
    Generate a single **valid** support ticket as a dict.

    The returned dict always passes TicketIn Pydantic validation.
    Pass `seed` for deterministic/reproducible output.
    """
    if seed is not None:
        random.seed(seed)
    return _build_base_ticket()


def generate_invalid_ticket(
    pattern: str | None = None,
    seed: int | None = None,
) -> dict:
    """
    Generate a ticket dict that **intentionally fails** TicketIn validation.

    Use `pattern` to force a specific corruption (one of INVALID_PATTERNS).
    Leave `pattern=None` to randomly pick a corruption each call.
    Pass `seed` for deterministic/reproducible output.
    """
    if seed is not None:
        random.seed(seed)

    ticket = _build_base_ticket()  # start from a valid base
    chosen = pattern if pattern is not None else random.choice(INVALID_PATTERNS)

    if chosen == "missing_subject":
        del ticket["subject"]
    elif chosen == "missing_body":
        del ticket["body"]
    elif chosen == "missing_ticket_id":
        del ticket["ticket_id"]
    elif chosen == "missing_timestamp":
        del ticket["timestamp"]
    elif chosen == "empty_subject":
        ticket["subject"] = ""
    elif chosen == "empty_body":
        ticket["body"] = ""
    elif chosen == "invalid_uuid":
        ticket["ticket_id"] = "not-a-valid-uuid"
    elif chosen == "malformed_timestamp":
        ticket["timestamp"] = "2024-13-99T99:99:99"
    else:
        raise ValueError(f"Unknown invalid pattern: {chosen!r}")

    return ticket
```

### Testing Pattern
```python
# tests/test_generator.py
import uuid
import pytest
from pydantic import ValidationError
from src.api.schemas import TicketIn
from src.simulator.generator import (
    generate_ticket,
    generate_invalid_ticket,
    QUEUES,
    TYPES,
    INVALID_PATTERNS,
)


# ── Valid ticket tests ──────────────────────────────────────────────

def test_output_validates_as_ticket_in():
    """Generated dict must pass TicketIn Pydantic validation."""
    ticket_dict = generate_ticket()
    ticket = TicketIn(**ticket_dict)
    assert ticket.subject  # non-empty
    assert ticket.body     # non-empty


def test_ticket_id_is_valid_uuid():
    result = generate_ticket()
    parsed = uuid.UUID(result["ticket_id"])  # raises ValueError if invalid
    assert parsed.version == 4


def test_language_in_allowed_set():
    for _ in range(20):
        result = generate_ticket()
        assert result["language"] in ["en", "de"]


def test_queue_in_allowed_set():
    for _ in range(20):
        result = generate_ticket()
        assert result["queue"] in QUEUES


def test_type_in_allowed_set():
    for _ in range(20):
        result = generate_ticket()
        assert result["type"] in TYPES


def test_seeded_output_is_reproducible():
    result_a = generate_ticket(seed=42)
    result_b = generate_ticket(seed=42)
    # ticket_id uses uuid4() — exclude from comparison
    assert result_a["subject"] == result_b["subject"]
    assert result_a["body"] == result_b["body"]
    assert result_a["language"] == result_b["language"]
    assert result_a["queue"] == result_b["queue"]
    assert result_a["type"] == result_b["type"]


def test_consecutive_calls_produce_unique_ticket_ids():
    result_a = generate_ticket()
    result_b = generate_ticket()
    assert result_a["ticket_id"] != result_b["ticket_id"]


# ── Invalid ticket tests ────────────────────────────────────────────

def test_invalid_ticket_always_fails_validation():
    """Random invalid ticket must ALWAYS raise ValidationError."""
    for _ in range(20):
        bad_dict = generate_invalid_ticket()
        with pytest.raises(ValidationError):
            TicketIn(**bad_dict)


@pytest.mark.parametrize("pattern", INVALID_PATTERNS)
def test_each_corruption_pattern_fails_validation(pattern):
    """Every specific corruption pattern must cause ValidationError."""
    bad_dict = generate_invalid_ticket(pattern=pattern)
    with pytest.raises(ValidationError):
        TicketIn(**bad_dict)
```

### Design Rationale — Why invalid tickets belong in the generator
The simulator acts as a **realistic data source** for an MLOps pipeline. Real-world data streams are never perfectly clean — payloads can be corrupted, truncated, or malformed. Generating invalid tickets here lets us:
1. **Verify the API's rejection logic** (FastAPI returns 422, not 500) against live traffic.
2. **Ensure zero invalid records enter PostgreSQL** — the DB must only contain Pydantic-validated data.
3. **Quantify the ingestion funnel** via Story 2.2 logs: `VALID=N, REJECTED=M` out of total sent.

The `generate_invalid_ticket()` function is a **test instrument**, not a bug. Its output is intentionally non-conformant.

### Scope Boundary — What NOT to do in this story
- **DO NOT** implement HTTP sending / requests library (Story 2.2)
- **DO NOT** implement drift mode / drift parameters (Story 2.2)
- **DO NOT** implement a CLI entrypoint or `argparse` (Story 2.2)
- **DO NOT** modify any files in `src/api/` — read-only dependency on `schemas.py`
- **DO NOT** add new packages to `requirements.txt` — `random`, `uuid`, `datetime` are all stdlib
- **DO NOT** suppress or catch `ValidationError` inside `generate_invalid_ticket()` — the caller (Story 2.2 or tests) decides what to do with the failed payload

### Project Structure Notes

- New files: `src/simulator/generator.py`, `tests/test_generator.py`
- Possible new file: `src/simulator/__init__.py` (create if missing — may be empty)
- No modifications to existing files needed
- After this story, `src/simulator/` has: `__init__.py`, `generator.py`
- `generator.py` exports: `generate_ticket()`, `generate_invalid_ticket()`, `QUEUES`, `TYPES`, `INVALID_PATTERNS`

### References

- [Source: epics.md - Epic 2, Story 2.1] — AC definition
- [Source: 02_domain_and_data_contract.md §2] — Ticket schema fields and types
- [Source: data_info.md] — Real domain values for Queue, Type, Language, and sample German/English text
- [Source: architecture.md §3] — Stream Simulator: script Python sinh request liên tục
- [Source: Story 1.2 Dev Agent Record] — TicketIn location and import path
- [Source: docs/project-context/02_domain_and_data_contract.md §7] — Language Drift: en/de distribution

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6 (Thinking) — bmad-dev-story workflow

### Debug Log References

- pytest run 1: `python -m pytest tests/test_generator.py -v` → **20 passed, 1 warning** (0.55s)
- pytest run 2 (regression): `python -m pytest tests/ -v` → **47 passed, 1 warning** (0.56s)

### Completion Notes List

- ✅ AC1: `generate_ticket()` trả dict hợp lệ với `TicketIn` schema (7 fields đầy đủ).
- ✅ AC2: Sử dụng pool template thực tế từ domain (IT Support, Billing, Security…).
- ✅ AC3: Language sampling 70% EN / 30% DE bằng `random.choices(weights=[70,30])`.
- ✅ AC4: `queue` sample từ 5 giá trị domain chính xác.
- ✅ AC5: `type` sample từ `["Incident","Request","Problem","Change"]`.
- ✅ AC6: `random.seed(seed)` cho kết quả deterministic trên subject/body/language/queue/type.
- ✅ AC7: 20 unit tests — 9 valid ticket tests + 11 invalid ticket tests — tất cả PASS.
- ✅ AC8: `generate_invalid_ticket(pattern=...)` hỗ trợ 8 corruption patterns. Mỗi pattern raise `ValidationError`. Pattern không hợp lệ raise `ValueError`.
- Design: `_build_base_ticket()` internal helper tách logic khỏi seeding để 2 public functions dùng chung.

### File List

- `src/simulator/__init__.py` [EXISTED — unchanged]
- `src/simulator/generator.py` [NEW]
- `tests/test_generator.py` [NEW]
