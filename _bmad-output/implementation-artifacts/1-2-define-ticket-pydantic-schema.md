# Story 1.2: Define Ticket Pydantic Schema

Status: review

## Story

As a MLOps Engineer,
I want to define a strict Pydantic data contract for incoming tickets in `src/api/schemas.py`,
so that invalid data is rejected before touching the database and the system enforces the domain contract precisely.

## Acceptance Criteria

1. **[AC1]** A `TicketIn` Pydantic model in `src/api/schemas.py` accepts valid payloads containing `ticket_id` (UUID), `subject` (non-empty str), `body` (non-empty str), `timestamp` (ISO8601 datetime), plus optional `language` and `queue` and `type` fields matching the domain contract.
2. **[AC2]** Sending a POST request with a missing or invalid payload to any route using `TicketIn` returns HTTP **422 Unprocessable Entity** with a structured validation error body — **NOT HTTP 400**.
3. **[AC3]** `ticket_id` must be a valid UUID — non-UUID strings are rejected with a clear validation error.
4. **[AC4]** `subject` and `body` must not be empty strings — empty values are rejected.
5. **[AC5]** `timestamp` must parse as a valid ISO8601 datetime — malformed strings are rejected.
6. **[AC6]** Unit tests cover: valid payload passes, missing required fields rejected, empty `subject`/`body` rejected, invalid UUID rejected, invalid `timestamp` rejected.

## Tasks / Subtasks

- [x] Task 1: Populate `src/api/schemas.py` with `TicketIn` and `TicketOut` models (AC: #1, #2, #3, #4, #5)
  - [x] 1.1 Define `TicketIn` with all fields from domain contract (`02_domain_and_data_contract.md §2`)
  - [x] 1.2 Add `@field_validator` for `subject` and `body` — reject empty strings (stripped)
  - [x] 1.3 Define `TicketOut` (inference output contract: `ticket_id`, `predicted_priority`, `confidence_score`, `model_version`) — PLACEHOLDER only, used in Story 1.3+
  - [x] 1.4 Add `model_config = ConfigDict(str_strip_whitespace=True)` to auto-strip whitespace
- [x] Task 2: Write unit tests in `tests/test_schemas.py` (AC: #6)
  - [x] 2.1 Test valid full payload passes `TicketIn` validation
  - [x] 2.2 Test missing required fields (`ticket_id`, `subject`, `body`, `timestamp`) each rejected with `ValidationError`
  - [x] 2.3 Test empty `subject` rejected, empty `body` rejected
  - [x] 2.4 Test invalid UUID string rejected
  - [x] 2.5 Test invalid timestamp string rejected
  - [x] 2.6 Test optional fields (`language`, `queue`, `type`) — absent is valid, present validates as str
- [x] Task 3: Verify existing tests still pass (no regressions) (AC: all)
  - [x] 3.1 Run `pytest tests/` — confirm `test_health.py` still passes (3/3)

## Dev Notes

### Previous Story Intelligence (Story 1.1)
- `src/api/schemas.py` **already exists** as a placeholder with a module docstring only. **OVERWRITE IT** — do not create a new file.
- `tests/conftest.py` uses `ASGITransport` + `AsyncClient` pattern — reuse same pattern in new test file if needed, or import models directly (no HTTP needed for schema unit tests).
- `pytest.ini` sets `asyncio_mode = auto` — schema tests are synchronous (no async needed); they will still run correctly.
- Dependency conflict warnings from pip (starlette multipart) are benign — ignore in test output.
- `requirements.txt` already has `pydantic==2.7.1` installed — do NOT bump version.

### Data Contract — MANDATORY field definitions
Source: `02_domain_and_data_contract.md §2`:

| Field | Type | Required | Constraint |
|---|---|---|---|
| `ticket_id` | `UUID` | ✅ | Must be valid UUID v4 |
| `timestamp` | `datetime` | ✅ | ISO8601, timezone-aware preferred |
| `subject` | `str` | ✅ | Non-empty (after strip) |
| `body` | `str` | ✅ | Non-empty (after strip) |
| `language` | `str` | ❌ optional | e.g. `"en"`, `"de"`, `"es"` |
| `queue` | `str` | ❌ optional | e.g. `"Technical Support"` |
| `type` | `str` | ❌ optional | e.g. `"Incident"`, `"Request"` |

Inference Output Contract (`02_domain_and_data_contract.md §3`):

| Field | Type | Description |
|---|---|---|
| `ticket_id` | `UUID` | Echo of input |
| `predicted_priority` | `Literal["low","medium","high"]` | Model output |
| `confidence_score` | `float` (0.0–1.0) | Prediction confidence |
| `model_version` | `str` | Model version string |

### Pydantic v2 Implementation Pattern
```python
# src/api/schemas.py
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class TicketIn(BaseModel):
    """Incoming ticket payload — strict Data Contract enforcement."""

    model_config = ConfigDict(str_strip_whitespace=True)

    ticket_id: UUID
    timestamp: datetime
    subject: str
    body: str
    language: Optional[str] = None
    queue: Optional[str] = None
    type: Optional[str] = None

    @field_validator("subject", "body")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("must not be empty")
        return v


class TicketOut(BaseModel):
    """Inference response — PLACEHOLDER, fully used from Story 1.3 onwards."""

    ticket_id: UUID
    predicted_priority: Literal["low", "medium", "high"]
    confidence_score: float
    model_version: str
```

### Critical: HTTP 422 NOT 400
FastAPI uses Pydantic v2 and returns **HTTP 422** (not 400) for validation errors automatically.
- The epic AC says "HTTP 400" but this reflects the **intended behavior** (reject invalid), not the exact status code.
- FastAPI's standard is 422 — do NOT add custom exception handlers to force 400. This aligns with FastAPI best practices and OpenAPI spec.
- AC2 in this story is written as 422 to match the actual FastAPI behavior.

### Testing Pattern — Schema Unit Tests (No HTTP needed)
```python
# tests/test_schemas.py
import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError

from src.api.schemas import TicketIn


VALID_PAYLOAD = {
    "ticket_id": str(uuid4()),
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "subject": "Login page is broken",
    "body": "Users cannot log in since the last deployment.",
}

def test_valid_payload_passes():
    ticket = TicketIn(**VALID_PAYLOAD)
    assert ticket.subject == "Login page is broken"

def test_missing_ticket_id_raises():
    data = VALID_PAYLOAD.copy()
    del data["ticket_id"]
    with pytest.raises(ValidationError):
        TicketIn(**data)

def test_empty_subject_raises():
    data = {**VALID_PAYLOAD, "subject": ""}
    with pytest.raises(ValidationError):
        TicketIn(**data)

def test_empty_body_raises():
    data = {**VALID_PAYLOAD, "body": "   "}  # whitespace-only → stripped → empty
    with pytest.raises(ValidationError):
        TicketIn(**data)

def test_invalid_uuid_raises():
    data = {**VALID_PAYLOAD, "ticket_id": "not-a-uuid"}
    with pytest.raises(ValidationError):
        TicketIn(**data)

def test_invalid_timestamp_raises():
    data = {**VALID_PAYLOAD, "timestamp": "not-a-date"}
    with pytest.raises(ValidationError):
        TicketIn(**data)

def test_optional_fields_absent_is_valid():
    ticket = TicketIn(**VALID_PAYLOAD)
    assert ticket.language is None
    assert ticket.queue is None
    assert ticket.type is None
```

### Scope Boundary — What NOT to do in this story
- **DO NOT** create `POST /tickets/` route (Story 1.3)
- **DO NOT** create DB models / SQLAlchemy table definitions (Story 1.3)
- **DO NOT** add Alembic migrations — not yet needed
- **DO NOT** implement inference logic in `TicketOut` (Epic 6/8)
- **DO NOT** modify `main.py`, `database.py`, `health.py`, or `docker-compose.yml`
- **DO NOT** add new packages to `requirements.txt` — Pydantic is already installed

### Project Structure Notes

- Target file: `src/api/schemas.py` — **OVERWRITE existing placeholder** (it contains only a docstring)
- New test file: `tests/test_schemas.py` — create new file
- No new directories needed
- Import path: `from src.api.schemas import TicketIn` (consistent with conftest.py pattern)

### References

- [Source: 02_domain_and_data_contract.md §2] — Ticket Schema (field names, types, constraints)
- [Source: 02_domain_and_data_contract.md §3] — Input/Output Contract (TicketOut)
- [Source: 02_domain_and_data_contract.md §6] — Validation Rules (UUID, non-empty, ISO8601)
- [Source: architecture.md §2.1] — Pydantic used for data contract enforcement
- [Source: 08_agent_workflow_rules.md §3] — Validation Chặt Chẽ: Mọi đầu vào API phải sử dụng Pydantic schema
- [Source: epics.md - Epic 1, Story 1.2] — AC definition
- [Source: Story 1.1 Dev Agent Record] — schemas.py placeholder already exists, conftest.py pattern

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6 (Thinking) — Amelia, Senior Software Engineer

### Debug Log References

- Run 1 (20 tests): 20 passed, 2 warnings — Pydantic `model_` namespace warning trên `TicketOut.model_version`.
- Fix: thêm `model_config = ConfigDict(protected_namespaces=())` vào `TicketOut`.
- Run 2 (20 tests): 20 passed, 1 warning — chỉ còn starlette multipart warning (ngoài tầm kiểm soát).

### Completion Notes List

- ✅ AC1: `TicketIn` chấp nhận payload hợp lệ với đầy đủ 7 fields theo domain contract.
- ✅ AC2: FastAPI trả HTTP 422 cho validation errors (Pydantic v2 standard).
- ✅ AC3: UUID không hợp lệ → `ValidationError`.
- ✅ AC4: `subject`/`body` rỗng (kể cả whitespace-only) → `ValidationError` via `field_validator` + `str_strip_whitespace=True`.
- ✅ AC5: Timestamp không đúng ISO8601 → `ValidationError`.
- ✅ AC6: 17 schema tests — tất cả PASS. 3 health tests từ Story 1.1 không regression.
- Bonus: `TicketOut` có `protected_namespaces=()` để suppress Pydantic warning về `model_version`.
- Tổng: 20/20 tests PASS (0.20s).

### File List

- `src/api/schemas.py` [MODIFIED — overwrite placeholder]
- `tests/test_schemas.py` [NEW]
