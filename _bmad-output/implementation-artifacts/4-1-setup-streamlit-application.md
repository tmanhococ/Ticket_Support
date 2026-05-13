# Story 4.1: Setup Streamlit Application

Status: review

## Story

As a Support Lead,
I want a basic web dashboard,
So that I can access the system through a UI instead of APIs.

## Acceptance Criteria

1. **[AC1]** The Streamlit app runs and is accessible via a URL (e.g., `http://localhost:8501`).
2. **[AC2]** The dashboard displays an application title (e.g., "Ticket Triage Stream") and a basic layout structure.
3. **[AC3]** The app connects successfully to the underlying PostgreSQL database (using the existing `DATABASE_URL` environment variable).
4. **[AC4]** The application code resides in `src/dashboard/`.
5. **[AC5]** A `Dockerfile` exists for the dashboard service and `docker-compose.yml` is updated to run the dashboard alongside the API and DB.

## Tasks / Subtasks

- [x] Task 1: Setup Streamlit project structure
  - [x] 1.1 Create `src/dashboard/` directory.
  - [x] 1.2 Add `streamlit`, `pandas`, `psycopg2-binary` to `requirements.txt`.
  - [x] 1.3 Create `src/dashboard/app.py` with basic layout and title.

- [x] Task 2: Implement Database Connection
  - [x] 2.1 Add database connection logic in `src/dashboard/app.py` (use `st.connection` or `SQLAlchemy` engine).
  - [x] 2.2 Verify connection by displaying a success message or running a simple test query.

- [x] Task 3: Dockerize the Dashboard
  - [x] 3.1 Create `src/dashboard/Dockerfile`.
  - [x] 3.2 Update `docker-compose.yml` to include the `dashboard` service.
  - [x] 3.3 Ensure the `dashboard` service can reach the `db` service.

## Dev Notes

### Architecture Compliance
- We use Streamlit for the dashboard.
- PostgreSQL is the backend database.
- The UI should be minimal and pragmatic.

### Web Research / Libraries
- Use Streamlit version 1.30+ for modern features.
- For database connections in Streamlit, consider using `st.connection("postgresql", type="sql")` with `psycopg2`, or standard `SQLAlchemy`.

### Git Intelligence
- Previously, we used Docker to containerize the `api`. We should ensure the dashboard is similarly Dockerized.

### File Structure Requirements
```text
src/dashboard/
├── app.py
├── Dockerfile
```

## Dev Agent Record

### Completion Notes
- ✅ AC1: Streamlit app runs and is accessible on port 8501 via docker-compose.
- ✅ AC2: App title and layout set up.
- ✅ AC3: Connected successfully to PostgreSQL using SQLAlchemy create_engine. Handled stripping of +asyncpg from DATABASE_URL.
- ✅ AC4: Code resides in `src/dashboard/`.
- ✅ AC5: Created `src/dashboard/Dockerfile` with `curl` for healthchecks and updated `docker-compose.yml` with the dashboard service.

### File List
- `requirements.txt` [MODIFIED - added streamlit, pandas, psycopg2-binary]
- `src/dashboard/app.py` [NEW]
- `src/dashboard/Dockerfile` [NEW]
- `docker-compose.yml` [MODIFIED - added dashboard service]

