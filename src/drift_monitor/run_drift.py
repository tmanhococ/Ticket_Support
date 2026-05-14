"""
src/drift_monitor/run_drift.py
--------------------------------
EvidentlyAI Data Drift Detection script for Ticket Triage MLOps.

Architecture (architecture.md §3 — Drift Monitor):
- Runs as a standalone container/cron job on EC2.
- Reads reference vs current data from PostgreSQL.
- Generates an HTML report using EvidentlyAI.
- Uploads the report to S3 (timestamped + 'latest' alias).

Usage:
    # One-shot mode (for testing / manual run)
    python -m src.drift_monitor.run_drift --once

    # Scheduled mode (runs every SCHEDULE_INTERVAL_HOURS hours)
    python -m src.drift_monitor.run_drift
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

try:
    from evidently.report import Report
    from evidently.metric_presets import DataDriftPreset, DataQualityPreset

    _EVIDENTLY_AVAILABLE = True
except ImportError:
    Report = None
    DataDriftPreset = None
    DataQualityPreset = None
    _EVIDENTLY_AVAILABLE = False

from src.drift_monitor.config import (
    REPORT_OUTPUT_DIR,
    SCHEDULE_INTERVAL_HOURS,
)
from src.drift_monitor.db_reader import DriftMonitorError, fetch_current_data, fetch_reference_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def generate_report(
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
    output_dir: str = REPORT_OUTPUT_DIR,
) -> str:
    """
    Generate an EvidentlyAI HTML drift report.

    Compares `reference_df` (baseline) against `current_df` (recent production).
    Report includes:
      - DataDriftPreset: checks distribution drift across all columns.
      - DataQualityPreset: checks for missing values, type issues.

    Args:
        reference_df: Baseline tickets DataFrame.
        current_df: Recent production tickets DataFrame.
        output_dir: Directory to write the HTML file.

    Returns:
        Absolute path to the generated HTML report file.

    Raises:
        RuntimeError: If EvidentlyAI report generation fails.
    """
    if Report is None:
        raise RuntimeError("evidently is not installed. Run: pip install evidently")

    # Select text columns relevant to drift detection
    columns_to_monitor = ["language", "queue", "type", "predicted_priority"]

    # Keep only columns that exist in both DataFrames
    available_cols = [
        c for c in columns_to_monitor if c in reference_df.columns and c in current_df.columns
    ]
    if not available_cols:
        raise RuntimeError(f"None of the target columns {columns_to_monitor} found in DataFrames.")

    ref = reference_df[available_cols].copy()
    curr = current_df[available_cols].copy()

    # Fill NaN values to avoid Evidently issues with nulls
    for col in available_cols:
        ref[col] = ref[col].fillna("unknown")
        curr[col] = curr[col].fillna("unknown")

    logger.info(
        "Running EvidentlyAI report: ref=%d rows, current=%d rows, cols=%s",
        len(ref),
        len(curr),
        available_cols,
    )

    report = Report(metrics=[DataDriftPreset(), DataQualityPreset()])
    report.run(reference_data=ref, current_data=curr)

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Timestamped filename
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"drift_report_{ts}.html"
    filepath = os.path.join(output_dir, filename)

    report.save_html(filepath)
    logger.info("Drift report saved to: %s", filepath)
    return filepath


def run_drift_job(engine=None) -> str:
    """
    End-to-end drift detection job:
      1. Fetch reference + current data from DB.
      2. Generate EvidentlyAI HTML report.
      3. Upload to S3 (timestamped + 'latest' alias).

    Args:
        engine: Optional SQLAlchemy engine (for testing injection).

    Returns:
        Path to the generated report HTML file.

    Raises:
        DriftMonitorError: If data fetch fails.
        RuntimeError: If report generation or S3 upload fails.
    """
    logger.info("=== Drift Monitor Job Started ===")

    # Step 1: Fetch data
    reference_df = fetch_reference_data(engine=engine)
    current_df = fetch_current_data(engine=engine)

    # Step 2: Generate report
    report_path = generate_report(reference_df, current_df)

    # Step 3: Upload to S3
    from src.api.utils.s3_client import upload_file as _upload_file

    # Timestamped copy
    ts_key = f"drift_reports/{os.path.basename(report_path)}"
    ts_uploaded = _upload_file(report_path, ts_key)

    # Latest alias (overwrite)
    latest_uploaded = _upload_file(report_path, "drift_reports/latest_drift_report.html")

    if ts_uploaded and latest_uploaded:
        logger.info("Drift report uploaded to S3: %s", ts_key)
    else:
        logger.warning(
            "S3 upload incomplete (ts=%s, latest=%s). Report saved locally at %s.",
            ts_uploaded,
            latest_uploaded,
            report_path,
        )

    logger.info("=== Drift Monitor Job Complete ===")
    return report_path


def _run_scheduled():
    """Run the drift job on a recurring schedule."""
    import schedule
    import time

    logger.info("Starting scheduled drift monitor (every %d hours).", SCHEDULE_INTERVAL_HOURS)

    # Run once immediately on startup, then on schedule
    try:
        run_drift_job()
    except (DriftMonitorError, RuntimeError) as exc:
        logger.error("Initial drift job failed: %s", exc)

    schedule.every(SCHEDULE_INTERVAL_HOURS).hours.do(_safe_run_job)

    while True:
        schedule.run_pending()
        time.sleep(60)


def _safe_run_job():
    """Wrapper that swallows exceptions to keep the scheduler alive."""
    try:
        run_drift_job()
    except (DriftMonitorError, RuntimeError) as exc:
        logger.error("Scheduled drift job failed: %s", exc)


def main():
    parser = argparse.ArgumentParser(description="Ticket Triage — Drift Monitor")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single drift report and exit (one-shot mode).",
    )
    args = parser.parse_args()

    if args.once:
        logger.info("Running in one-shot mode.")
        try:
            report_path = run_drift_job()
            logger.info("One-shot complete. Report at: %s", report_path)
            sys.exit(0)
        except (DriftMonitorError, RuntimeError) as exc:
            logger.error("One-shot drift job failed: %s", exc)
            sys.exit(1)
    else:
        _run_scheduled()


if __name__ == "__main__":
    main()
