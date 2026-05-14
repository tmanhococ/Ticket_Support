# Story 9.2: Automate and Upload Drift Reports

As a MLOps Engineer,
I want the drift report generation to run automatically and save to S3,
So that the dashboard can always access the latest report.

## Acceptance Criteria

1. **[AC1]** The `run_drift.py` script is updated to upload the generated HTML report to the configured AWS S3 bucket using the S3 client built in Epic 5.
2. **[AC2]** The uploaded file has a timestamped naming convention (e.g., `drift_report_YYYYMMDD_HHMMSS.html`) and potentially overwrites a `latest_drift_report.html` for easy dashboard access.
3. **[AC3]** Set up a scheduling mechanism (like `schedule` package or cron) to run the drift generation script automatically at regular intervals.
4. **[AC4]** Create or update Docker configuration to run the drift monitor service as a persistent background container.

## Tasks / Subtasks

- [x] Task 1: S3 Upload Integration
  - [x] 1.1 Import and use the S3 client from `src.api.utils.s3_client` (reused existing, no refactor needed).
  - [x] 1.2 Update `run_drift.py` to upload the generated HTML file to S3 after creation.
- [x] Task 2: Automation / Scheduling
  - [x] 2.1 Add a scheduler loop in `run_drift.py` using `schedule` library (every `SCHEDULE_INTERVAL_HOURS` hours).
  - [x] 2.2 Support running in both "one-shot" mode (`--once` flag) and "scheduled" mode (default infinite loop).
- [x] Task 3: Dockerization & Deployment
  - [x] 3.1 Update `docker-compose.yml` to include a `drift-monitor` service.
  - [x] 3.2 Create `src/drift_monitor/Dockerfile` (reuses base Python image with different CMD).

## Dev Notes

- **Architecture Compliance:** Automation is key for zero-touch deployment. Uploading to S3 enables the Streamlit dashboard (Epic 11) to display the report without sharing local filesystems.
- **S3 Upload Strategy:** Two uploads per run — timestamped key (`drift_reports/drift_report_YYYYMMDD_HHMMSS.html`) for history, plus `drift_reports/latest_drift_report.html` overwrite for easy dashboard access.
- **Scheduler:** Uses `schedule` library with `SCHEDULE_INTERVAL_HOURS` (default: 6h). Runs once immediately on startup, then on schedule. Exceptions are caught by `_safe_run_job` wrapper to keep container alive.
- **One-shot Mode:** `python -m src.drift_monitor.run_drift --once` — exits with code 0 on success, 1 on failure.
- **Resilience:** `_safe_run_job` wrapper catches all `DriftMonitorError` and `RuntimeError` to prevent container crash on single report failure.

## File List
- `src/drift_monitor/run_drift.py` — updated with S3 upload + scheduler + `--once` CLI flag
- `src/drift_monitor/Dockerfile` — new, standalone container for drift monitor
- `docker-compose.yml` — added `drift-monitor` service with all env vars
- `.env.example` — added Epic 9 env var documentation
- `tests/test_drift_monitor.py` — 4 S3 upload tests + 2 scheduler resilience tests

## Change Log
- 2026-05-14: Story created.
- 2026-05-14: Implementation complete. S3 upload (timestamped + latest alias), `--once`/scheduled modes, Dockerfile, docker-compose service, .env.example docs. 4 upload tests + 2 scheduler tests pass (16 total in file).

## Status

**Status:** review
