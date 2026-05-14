# Story 9.1: Generate EvidentlyAI Report

As a MLOps Engineer,
I want a script that compares recent tickets against baseline data,
So that I can detect data drift.

## Acceptance Criteria

1. **[AC1]** Create `src/drift_monitor/run_drift.py` that fetches a reference dataset (e.g., initial baseline) and current production data from the PostgreSQL database.
2. **[AC2]** The script executes EvidentlyAI to calculate drift metrics, specifically Data Drift and Text Classification Drift (or relevant text metrics).
3. **[AC3]** The script generates an HTML report showing the drift results and saves it locally.
4. **[AC4]** Write unit tests mocking the database connection and verifying the Evidently report generation logic runs without errors.

## Tasks / Subtasks

- [x] Task 1: Setup Drift Monitor Component
  - [x] 1.1 Create `src/drift_monitor/run_drift.py` and `src/drift_monitor/config.py`.
  - [x] 1.2 Implement database connection logic to fetch reference and current data using SQLAlchemy.
- [x] Task 2: Implement EvidentlyAI Logic
  - [x] 2.1 Integrate `evidently` library to calculate data drift on text and predicted labels.
  - [x] 2.2 Generate and save the HTML report to a local temporary directory.
- [x] Task 3: Unit Testing
  - [x] 3.1 Create `tests/test_drift_monitor.py`.
  - [x] 3.2 Mock database interactions and test the `run_drift` function.

## Dev Notes

- **Architecture Compliance:** Epic 9 focuses on Data Drift Detection using EvidentlyAI. The script runs standalone and connects to the existing PostgreSQL database via synchronous SQLAlchemy (psycopg2).
- **Dependencies:** `evidently==0.4.30`, `schedule==1.2.1`, `pandas` added to requirements.txt.
- **Data Selection:** Current window = last 24h (`CURRENT_WINDOW_HOURS`); reference = oldest 500 tickets (`REFERENCE_SAMPLE_SIZE`). Both are env-configurable.
- **Columns Monitored:** `language`, `queue`, `type`, `predicted_priority` — categorical text fields most likely to drift.

## File List
- `src/drift_monitor/run_drift.py` — core drift detection script
- `src/drift_monitor/config.py` — environment-based configuration
- `src/drift_monitor/db_reader.py` — synchronous DB reader (fetch_reference_data, fetch_current_data)
- `tests/test_drift_monitor.py` — 16 unit tests (all passing)
- `requirements.txt` — added evidently==0.4.30, schedule==1.2.1

## Change Log
- 2026-05-14: Story created.
- 2026-05-14: Implementation complete. `run_drift.py`, `db_reader.py`, `config.py` created. 6 DB reader tests + 4 generate_report tests all pass. `evidently==0.4.30` and `schedule==1.2.1` added to requirements.

## Status

**Status:** review
