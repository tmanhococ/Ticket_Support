# Story 1.3: Create Intake Endpoint & DB Save

Status: review

## Story

As a MLOps Engineer,
I want a `POST /tickets/` endpoint that validates incoming ticket payloads and saves them to PostgreSQL,
so that the system can continuously ingest simulated traffic from the Stream Simulator.

## Acceptance Criteria

1. **[AC1]** `POST /tickets/` accepts a valid JSON payload matching `TicketIn` schema and returns HTTP **201 Created** with the saved ticket's `ticket_id` and `timestamp`.
2. **[AC2]** Invalid payloads (missing required fields, bad UUID, empty subject/body) return HTTP **422 Unprocessable Entity** automatically via Pydantic — no manual handling needed.
3. **[AC3]** Each valid ticket is persisted to the PostgreSQL `tickets` table with columns: `ticket_id` (PK), `subject`, `body`, `timestamp`, `language`, `queue`, `type`, `received_at` (server-side timestamp).
4. **[AC4]** If the DB write fails (e.g. connection lost mid-request), the endpoint catches the exception and returns HTTP **503 Service Unavailable** with `{"detail": "storage_unavailable"}` — never HTTP 500.
5. **[AC5]** The `/health` endpoint (Story 1.1) continues to return HTTP 200 — no regression.
6. **[AC6]** Unit tests cover: valid POST returns 201, invalid payload returns 422, DB write failure returns 503 (mocked).

## Tasks / Subtasks

- [x] Task 1: Create `Ticket` SQLAlchemy ORM model in `src/api/models.py` (AC: #3)
  - [x] 1.1 Define `Ticket` table with all columns from AC3 using `DeclarativeBase`
  - [x] 1.2 Add `received_at` server-side default via `func.now()`
  - [x] 1.3 Create `src/api/models.py` (new file — does NOT exist yet)
- [x] Task 2: Create DB table on startup in `src/api/database.py` (AC: #3)
  - [x] 2.1 Add `create_tables()` async function that runs `metadata.create_all()` via engine
  - [x] 2.2 Call `create_tables()` inside the lifespan startup in `src/api/main.py`
- [x] Task 3: Create intake router `src/api/routes/tickets.py` (AC: #1, #2, #4)
  - [x] 3.1 `POST /tickets/` → accepts `TicketIn`, calls DB save, returns `{"ticket_id": ..., "timestamp": ...}` with status 201
  - [x] 3.2 Wrap DB insert in `try-except`; on failure return HTTP 503 with `{"detail": "storage_unavailable"}`
  - [x] 3.3 Use `Annotated[AsyncSession, Depends(get_db)]` dependency injection pattern
- [x] Task 4: Register tickets router in `src/api/main.py` (AC: #1)
  - [x] 4.1 Import and `include_router(tickets.router)` — do NOT break existing health router
- [x] Task 5: Write integration tests in `tests/test_tickets.py` (AC: #6)
  - [x] 5.1 Test valid POST returns 201 and correct JSON body (mock DB session)
  - [x] 5.2 Test invalid payload (missing `subject`) returns 422
  - [x] 5.3 Test DB write failure returns 503 (mock session to raise `SQLAlchemyError`)
- [x] Task 6: Run full test suite — no regressions (AC: #5)
  - [x] 6.1 `pytest tests/` — all 20 existing tests still pass + new tests pass

### Review Findings

- [ ] [Review][Patch] `TicketIn` lacks `max_length` constraints matching DB columns (`subject`, `language`, `queue`, `type`), causing length validation failures to trigger 503 instead of 422. [`src/api/schemas.py`]
- [x] [Review][Defer] Enforce timezone-aware datetimes explicitly (`AwareDatetime` instead of `datetime`) to prevent naive datetime storage issues. [`src/api/schemas.py`] — deferred, pre-existing

## Dev Notes

### Previous Story Intelligence
**Story 1.1 — Established patterns (MUST reuse, do NOT reinvent):**
- `database.py` already has: `engine`, `AsyncSessionLocal`, `get_db()`, `check_db_connection()` — **do NOT modify these**
- `get_db()` is the FastAPI dependency for DB session injection. Pattern: `Annotated[AsyncSession, Depends(get_db)]`
- `main.py` lifespan: startup logs, graceful DB error handling — ADD `create_tables()` call here, do NOT restructure
- Router pattern: import router object, `app.include_router(router)` — follow same pattern as `health.router`

**Story 1.2 — Schema patterns (MUST import, do NOT redefine):**
- `TicketIn` is in `src/api/schemas.py` — import from there, never redefine
- `TicketOut` is also in `schemas.py` — NOT used in this story (shadow mode = Epic 8)
- `str_strip_whitespace=True` already applied — whitespace-only strings already rejected before hitting the route

**Testing pattern from Story 1.1 (`conftest.py`):**
- `ASGITransport` + `AsyncClient` fixture named `client` — extend this fixture, do NOT duplicate
- `patch()` with `AsyncMock` for async DB functions — same pattern for mocking DB session

### DB Model Pattern — SQLAlchemy 2.x Declarative Style
```python
# src/api/models.py
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True
    )
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    queue: Mapped[str | None] = mapped_column(String(100), nullable=True)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

### `create_tables()` function — add to `database.py`
```python
# Append to src/api/database.py
from src.api.models import Base   # import after Base defined to avoid circular

async def create_tables() -> None:
    """Create all ORM-defined tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

⚠️ **Circular import warning**: `database.py` must import `Base` from `models.py`. `models.py` must NOT import from `database.py`. Keep the dependency one-way: `database.py → models.py`.

### Lifespan update in `main.py`
```python
# Modify the lifespan in src/api/main.py — add create_tables() call
from src.api.database import engine, create_tables   # add create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Ticket Triage API — connecting to DB...")
    try:
        await create_tables()                         # ← ADD THIS
        logger.info("DB tables ensured / connection pool initialised.")
    except Exception as exc:
        logger.warning("DB unavailable at startup (will retry per-request): %s", exc)
    yield
    logger.info("Shutting down — disposing DB connection pool...")
    await engine.dispose()
```

### Intake Route Pattern
```python
# src/api/routes/tickets.py
from typing import Annotated
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import get_db
from src.api.models import Ticket
from src.api.schemas import TicketIn

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/", status_code=201, summary="Ingest a support ticket")
async def create_ticket(
    payload: TicketIn,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Validate and persist an incoming ticket.
    Returns 201 with ticket_id and timestamp on success.
    Returns 503 on DB write failure (never 500).
    """
    ticket = Ticket(
        ticket_id=payload.ticket_id,
        subject=payload.subject,
        body=payload.body,
        timestamp=payload.timestamp,
        language=payload.language,
        queue=payload.queue,
        type=payload.type,
    )
    try:
        db.add(ticket)
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=503, detail="storage_unavailable") from exc
    return {"ticket_id": str(payload.ticket_id), "timestamp": payload.timestamp.isoformat()}
```

### Testing Pattern — Mock DB Session
```python
# tests/test_tickets.py
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone
import pytest
from sqlalchemy.exc import SQLAlchemyError

VALID_TICKET = {
    "ticket_id": str(uuid4()),
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "subject": "Cannot login",
    "body": "Users cannot log in since deployment.",
}

@pytest.mark.asyncio
async def test_create_ticket_returns_201(client):
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    with patch("src.api.routes.tickets.get_db", return_value=mock_session):
        response = await client.post("/tickets/", json=VALID_TICKET)
    assert response.status_code == 201
    assert "ticket_id" in response.json()

@pytest.mark.asyncio
async def test_invalid_payload_returns_422(client):
    response = await client.post("/tickets/", json={"subject": "only subject"})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_db_failure_returns_503(client):
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock(side_effect=SQLAlchemyError("DB down"))
    mock_session.rollback = AsyncMock()
    with patch("src.api.routes.tickets.get_db", return_value=mock_session):
        response = await client.post("/tickets/", json=VALID_TICKET)
    assert response.status_code == 503
    assert response.json()["detail"] == "storage_unavailable"
```

⚠️ **Note on mocking `get_db` dependency**: FastAPI dependency injection requires overriding via `app.dependency_overrides[get_db] = lambda: mock_session` rather than patching directly. Use `conftest.py` pattern or override inside the test. See implementation note below.

### Correct FastAPI Dependency Override Pattern for Tests
```python
# Preferred pattern — use app.dependency_overrides in conftest or test
from src.api.database import get_db
from src.api.main import app

async def override_get_db_ok():
    mock = AsyncMock()
    mock.commit = AsyncMock()
    mock.add = MagicMock()
    yield mock

async def override_get_db_fail():
    mock = AsyncMock()
    mock.commit = AsyncMock(side_effect=SQLAlchemyError("down"))
    mock.rollback = AsyncMock()
    mock.add = MagicMock()
    yield mock

# In test:
app.dependency_overrides[get_db] = override_get_db_ok
response = await client.post("/tickets/", json=VALID_TICKET)
app.dependency_overrides.clear()
```

### Scope Boundary — What NOT to do in this story
- **DO NOT** implement model inference / `predicted_priority` in this endpoint (Epic 8 — Shadow Mode)
- **DO NOT** save raw ticket JSON to S3 (Epic 5)
- **DO NOT** add Alembic migrations — `create_all()` is sufficient for Sprint 1
- **DO NOT** implement `GET /tickets/` listing endpoint (Epic 4 — Dashboard uses DB directly)
- **DO NOT** add API key auth (NFR6 — deferred to later)
- **DO NOT** modify `schemas.py`, `health.py`, or `docker-compose.yml`

### Project Structure Notes

- New files: `src/api/models.py`, `src/api/routes/tickets.py`, `tests/test_tickets.py`
- Modified files: `src/api/database.py` (add `create_tables()`), `src/api/main.py` (add import + lifespan call)
- `src/api/routes/tickets.py` must be imported and registered in `main.py` — follow exact pattern of `health.router`
- After this story, `src/api/routes/` has: `__init__.py`, `health.py`, `tickets.py`

### References

- [Source: epics.md - Epic 1, Story 1.3] — AC definition
- [Source: 02_domain_and_data_contract.md §2] — Ticket schema columns
- [Source: 02_domain_and_data_contract.md §4] — Data Flow: Intake API validates → saves to DB
- [Source: architecture.md §2.1, §2.2] — FastAPI + PostgreSQL async pattern
- [Source: 04_environment_and_deployment.md §5] — Fallback: never HTTP 500, return 503 on DB error
- [Source: 08_agent_workflow_rules.md §3] — Error Handling: try-except bắt buộc, fallback mandatory
- [Source: Story 1.1 Dev Agent Record] — `get_db()` pattern, `main.py` lifespan structure, router registration
- [Source: Story 1.2 Dev Agent Record] — `TicketIn` location and import path

## Dev Agent Record

### Agent Model Used

Gemini 3.1 Pro (High) — Amelia, Senior Software Engineer

### Debug Log References

- Pytest ran successfully with 27 passed tests, showing no regressions and confirming ACs for Story 1.3 are met.

### Completion Notes List

- ✅ AC1: `POST /tickets/` created, accepts valid payload and returns 201 with ticket_id and timestamp.
- ✅ AC2: Covered implicitly by FastAPI and `TicketIn` Pydantic model (returns 422). Added test case to ensure.
- ✅ AC3: `Ticket` SQLAlchemy model created with required columns.
- ✅ AC4: Try-except wrapper catches `SQLAlchemyError`, rollbacks, and throws 503 `storage_unavailable`.
- ✅ AC5: Health endpoint remains untouched and passes regression tests.
- ✅ AC6: Integration tests added via `app.dependency_overrides` mock `get_db`.

### File List

- `src/api/models.py` [NEW]
- `src/api/database.py` [MODIFIED]
- `src/api/main.py` [MODIFIED]
- `src/api/routes/tickets.py` [NEW]
- `tests/test_tickets.py` [NEW]
