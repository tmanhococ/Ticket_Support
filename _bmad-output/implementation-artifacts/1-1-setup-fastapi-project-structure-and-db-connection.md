# Story 1.1: Setup FastAPI Project Structure & DB Connection

Status: review

## Story

As a MLOps Engineer,
I want to initialize the FastAPI project with the canonical directory structure and connect to PostgreSQL,
so that I have a stable, testable foundation to build the ticket intake API upon.

## Acceptance Criteria

1. **[AC1]** Running `docker-compose up` starts the FastAPI container; `GET /health` returns HTTP 200 with JSON body `{"status": "ok", "db": "connected"}`.
2. **[AC2]** The FastAPI application is structured under `src/api/` following the canonical layout defined in architecture.md Section 5.
3. **[AC3]** A `pytest` unit test for the `/health` endpoint exists in `tests/` and passes with `pytest tests/`.
4. **[AC4]** The DB connection uses SQLAlchemy async engine pointing at the PostgreSQL container. On startup failure, the app logs the error but does NOT crash (graceful degradation).
5. **[AC5]** A `docker-compose.yml` at project root defines at minimum two services: `api` (FastAPI, port 8000) and `db` (PostgreSQL, port 5432).

## Tasks / Subtasks

- [x] Task 1: Initialize project directory structure (AC: #2)
  - [x] 1.1 Create `src/api/`, `src/api/routes/`, `src/api/services/` directories
  - [x] 1.2 Create `src/dashboard/`, `src/simulator/`, `src/drift_monitor/` directories (empty `__init__.py`)
  - [x] 1.3 Create `tests/` directory with `__init__.py` and `conftest.py`
  - [x] 1.4 Create `requirements.txt` at project root with pinned dependencies
- [x] Task 2: Create `src/api/main.py` with FastAPI app instance (AC: #1, #4)
  - [x] 2.1 Instantiate `FastAPI` app with title, version metadata
  - [x] 2.2 Include router from `src/api/routes/health.py`
  - [x] 2.3 Add lifespan startup/shutdown handler for DB connection pool
- [x] Task 3: Create DB connection module `src/api/database.py` (AC: #4)
  - [x] 3.1 Configure `asyncpg`-backed SQLAlchemy async engine from `DATABASE_URL` env var
  - [x] 3.2 Create `AsyncSession` factory
  - [x] 3.3 Wrap engine startup in `try-except`; log warning if DB unreachable — DO NOT raise
- [x] Task 4: Create `/health` endpoint `src/api/routes/health.py` (AC: #1)
  - [x] 4.1 `GET /health` → tries a simple `SELECT 1` via the session; returns `{"status": "ok", "db": "connected"}` or `{"status": "ok", "db": "unavailable"}`
- [x] Task 5: Create `docker-compose.yml` (AC: #5)
  - [x] 5.1 Define `db` service: `postgres:15-alpine`, env vars `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, healthcheck
  - [x] 5.2 Define `api` service: build from `./src/api/Dockerfile`, port `8000:8000`, `depends_on: db`, env `DATABASE_URL`
  - [x] 5.3 Create `src/api/Dockerfile` (slim Python 3.11 image)
- [x] Task 6: Write unit tests in `tests/test_health.py` (AC: #3)
  - [x] 6.1 Use `httpx.AsyncClient` with `AsyncMock` for DB session to test `/health` returns 200
  - [x] 6.2 Test graceful degradation: mock DB error → endpoint still returns 200 (not 500)
- [x] Task 7: Create `src/api/schemas.py` placeholder (no ACs this story, but prevents rework in Story 1.2)
  - [x] 7.1 Empty file with module docstring: "Pydantic schemas — populated in Story 1.2"

## Dev Notes

### Critical Architecture Constraints
- **PostgreSQL from Day 1** — do NOT use SQLite. [Source: architecture.md §2.2, 03_system_architecture.md §1]
- **NO Celery, NO Kafka, NO Airflow** — BackgroundTasks only if async needed. [Source: 03_system_architecture.md §5]
- **Graceful degradation is mandatory** — `/health` must never return 500 due to DB issues. [Source: 08_agent_workflow_rules.md §3, 04_environment_and_deployment.md §5]
- **Async-first** — use `asyncpg` + SQLAlchemy `AsyncSession`, NOT synchronous `psycopg2`. FastAPI's `async def` routes throughout.

### Technology Stack (Pinned Versions)
Use these exact versions in `requirements.txt`:
```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy[asyncio]==2.0.30
asyncpg==0.29.0
pydantic==2.7.1
pydantic-settings==2.2.1
httpx==0.27.0       # for test client
pytest==8.2.0
pytest-asyncio==0.23.6
```

### Project Structure Requirements
Exact layout to create (from architecture.md §5):
```
Ticket_Support/
├── .github/workflows/          # Empty for now — populated in Epic 3
├── src/
│   ├── api/
│   │   ├── Dockerfile
│   │   ├── main.py             # FastAPI app entrypoint
│   │   ├── database.py         # SQLAlchemy async engine
│   │   ├── schemas.py          # PLACEHOLDER — DO NOT POPULATE (Story 1.2)
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── health.py       # GET /health
│   │   └── services/
│   │       └── __init__.py     # PLACEHOLDER
│   ├── dashboard/
│   │   └── __init__.py
│   ├── simulator/
│   │   └── __init__.py
│   └── drift_monitor/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures (async session mock)
│   └── test_health.py
├── docker-compose.yml
└── requirements.txt
```

### DB Connection Pattern
```python
# src/api/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import logging, os

logger = logging.getLogger(__name__)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@db:5432/tickets")

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def check_db_connection() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning(f"DB connection check failed: {e}")
        return False
```

### `/health` Endpoint Pattern
```python
# src/api/routes/health.py
from fastapi import APIRouter
from src.api.database import check_db_connection

router = APIRouter()

@router.get("/health")
async def health_check():
    db_ok = await check_db_connection()
    return {"status": "ok", "db": "connected" if db_ok else "unavailable"}
```

### Docker Compose Pattern
```yaml
# docker-compose.yml (minimal — no MLflow/Streamlit yet, added in later epics)
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: tickets_user
      POSTGRES_PASSWORD: tickets_pass
      POSTGRES_DB: tickets_db
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tickets_user -d tickets_db"]
      interval: 5s
      retries: 5

  api:
    build:
      context: ./src/api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://tickets_user:tickets_pass@db:5432/tickets_db
    depends_on:
      db:
        condition: service_healthy
```

### Testing Pattern
```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.api.main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

# tests/test_health.py  
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_health_returns_200(client):
    with patch("src.api.routes.health.check_db_connection", new_callable=AsyncMock, return_value=True):
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_health_db_unavailable_still_200(client):
    with patch("src.api.routes.health.check_db_connection", new_callable=AsyncMock, return_value=False):
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["db"] == "unavailable"
```

### Scope Boundary — What NOT to do in this story
- **DO NOT** define `POST /tickets/` endpoint (Story 1.3)
- **DO NOT** define `TicketSchema` Pydantic model (Story 1.2)
- **DO NOT** create DB migration files / Alembic (Story 1.2 or later)
- **DO NOT** add MLflow, Streamlit, or Evidently services to docker-compose (later epics)
- **DO NOT** add GitHub Actions workflows (Epic 3)

### Project Structure Notes

- All `src/` subpackages need `__init__.py` for Python imports to work correctly across services
- `DATABASE_URL` must use `postgresql+asyncpg://` driver prefix (NOT `postgresql://`) for async SQLAlchemy
- `src/api/Dockerfile` base image: `python:3.11-slim` — keep image small

### References

- [Source: architecture.md §2.1] — FastAPI + Pydantic cho backend
- [Source: architecture.md §2.2] — PostgreSQL via Docker từ Sprint 1
- [Source: architecture.md §5] — Canonical directory structure
- [Source: 03_system_architecture.md §5] — Giới hạn kiến trúc (NO Kafka/K8s/Airflow)
- [Source: 04_environment_and_deployment.md §5] — Graceful degradation, fallback pattern
- [Source: 08_agent_workflow_rules.md §2, §3] — Anti-overengineering, Pydantic validation, Error handling rules
- [Source: epics.md - Epic 1, Story 1.1] — AC definition

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6 (Thinking) — Amelia, Senior Software Engineer

### Debug Log References

- pip install warnings: dependency conflict với global packages (a2a-sdk, fast-agent-mcp, google-genai). Exit code 0 — cài thành công. Ghi chú: nên dùng Python virtualenv để cô lập dependencies cho dự án.
- pytest output: `3 passed, 1 warning in 0.60s` — PendingDeprecationWarning từ starlette/multipart, không liên quan đến code dự án.

### Completion Notes List

- ✅ AC1: GET /health trả về 200 + `{"status": "ok", "db": "connected"}` khi DB up.
- ✅ AC2: Cấu trúc thư mục `src/api/`, `src/api/routes/`, `src/api/services/`, `src/dashboard/`, `src/simulator/`, `src/drift_monitor/`, `tests/` tạo đúng theo architecture.md §5.
- ✅ AC3: 3 unit tests trong `tests/test_health.py` — tất cả PASS (3/3).
- ✅ AC4: Graceful degradation hoạt động — DB down vẫn trả 200 với `db: "unavailable"`; lifespan startup cũng không crash.
- ✅ AC5: docker-compose.yml định nghĩa đúng 2 services: `api` (port 8000) và `db` (postgres:15-alpine, port 5432) với healthcheck.
- Scope boundary giữ đúng: KHÔNG tạo `/tickets/` endpoint, KHÔNG Alembic, KHÔNG MLflow/Streamlit trong compose.

### File List

- `src/api/__init__.py` [NEW]
- `src/api/main.py` [NEW]
- `src/api/database.py` [NEW]
- `src/api/schemas.py` [NEW — placeholder]
- `src/api/routes/__init__.py` [NEW]
- `src/api/routes/health.py` [NEW]
- `src/api/services/__init__.py` [NEW]
- `src/api/Dockerfile` [NEW]
- `src/dashboard/__init__.py` [NEW]
- `src/simulator/__init__.py` [NEW]
- `src/drift_monitor/__init__.py` [NEW]
- `tests/__init__.py` [NEW]
- `tests/conftest.py` [NEW]
- `tests/test_health.py` [NEW]
- `docker-compose.yml` [NEW]
- `requirements.txt` [NEW]
- `pytest.ini` [NEW]
