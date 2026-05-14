# Story 5.1: Optimize PostgreSQL configuration

As a MLOps Engineer,
I want to optimize PostgreSQL configuration,
So that the database can handle concurrent inserts from the simulator effectively.

## Acceptance Criteria

1. **[AC1]** The database connection URL is configured to support connection pooling.
2. **[AC2]** The FastAPI application uses a connection pool (e.g. SQLAlchemy QueuePool) explicitly configured with size and overflow parameters.
3. **[AC3]** The Streamlit application connects to the database using an efficient connection state.
4. **[AC4]** Under simulated high load (50 requests/sec), no "too many clients already" connection errors are thrown by PostgreSQL.

## Tasks / Subtasks

- [x] Task 1: Configure Connection Pooling in FastAPI
  - [x] 1.1 Update `src/api/database.py` to use SQLAlchemy `QueuePool` with optimal `pool_size` and `max_overflow`.
  - [x] 1.2 Validate that the database session management correctly releases connections back to the pool.
- [x] Task 2: Verify Connection Configuration in Streamlit
  - [x] 2.1 Update `src/dashboard/app.py` or relevant DB connection scripts to ensure Streamlit connection handles concurrency appropriately.
- [x] Task 3: Load Testing & Verification
  - [x] 3.1 Run the Stream Simulator at max load.
  - [x] 3.2 Verify database stability and check logs for connection errors.

## Dev Notes

- **Business Context:** With the Simulator generating traffic (up to 50 requests/sec), PostgreSQL needs to handle high concurrency efficiently. Connection pooling prevents connection exhaustion and improves performance.
- **Architecture Compliance:** Adhere to the "1-person execution" rule. Keep infrastructure minimal. SQLAlchemy pooling is preferred over spinning up a new container (like PgBouncer) unless absolutely necessary.
- **Technical Hints:** For SQLAlchemy, pass `pool_size=...` and `max_overflow=...` directly into `create_engine()`.

## Dev Agent Record
- **Completion Notes:** Story implemented completely. Configured FastAPI `create_async_engine` with `pool_size=20` and `max_overflow=10`. Configured Streamlit DB engine with `pool_size=10` and `max_overflow=5`. Verified simulated load handles concurrency without "too many clients" exceptions due to the SQLAlchemy QueuePool.

## Change Log
- Updated `src/api/database.py`.
- Updated `src/dashboard/app.py`.
- Date: 2026-05-13/14

## Status

**Status:** review
