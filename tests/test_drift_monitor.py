"""
tests/test_drift_monitor.py
-----------------------------
Unit tests for Epic 9 — Data Drift Detection.

Story 9.1 tests:
  - fetch_reference_data / fetch_current_data (mocked DB)
  - generate_report (mocked Evidently)
  - DriftMonitorError raised when data is insufficient

Story 9.2 tests:
  - run_drift_job with mocked DB + S3
  - S3 upload key naming (timestamped + 'latest')
  - Scheduler resilience (exception swallowed, does not crash)
"""

import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, call

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

REFERENCE_ROWS = [
    {
        "ticket_id": f"aaaa-{i:04d}",
        "subject": f"Issue {i}",
        "body": f"Body text {i}",
        "language": "en",
        "queue": "Technical Support",
        "type": "Incident",
        "predicted_priority": "medium",
        "received_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
    }
    for i in range(50)
]

CURRENT_ROWS = [
    {
        "ticket_id": f"bbbb-{i:04d}",
        "subject": f"Neues Problem {i}",
        "body": f"Beschreibung {i}",
        "language": "de",
        "queue": "Technical Support",
        "type": "Incident",
        "predicted_priority": "high",
        "received_at": datetime(2024, 2, 1, tzinfo=timezone.utc),
    }
    for i in range(30)
]


def _make_df(rows):
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Story 9.1 — DB Reader tests
# ---------------------------------------------------------------------------


class TestFetchReferenceData:
    """Tests for fetch_reference_data with mocked DB engine."""

    def test_returns_dataframe_on_success(self):
        """Should return a DataFrame with correct columns."""
        from src.drift_monitor.db_reader import fetch_reference_data

        mock_engine = MagicMock()
        expected_df = _make_df(REFERENCE_ROWS)

        with patch("src.drift_monitor.db_reader.pd.read_sql", return_value=expected_df):
            df = fetch_reference_data(engine=mock_engine, sample_size=50)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 50
        assert "language" in df.columns

    def test_raises_when_empty(self):
        """Should raise DriftMonitorError when DB returns empty result."""
        from src.drift_monitor.db_reader import fetch_reference_data, DriftMonitorError

        mock_engine = MagicMock()
        with patch("src.drift_monitor.db_reader.pd.read_sql", return_value=pd.DataFrame()):
            with pytest.raises(DriftMonitorError, match="empty"):
                fetch_reference_data(engine=mock_engine)

    def test_raises_on_db_error(self):
        """Should wrap SQLAlchemy exceptions in DriftMonitorError."""
        from src.drift_monitor.db_reader import fetch_reference_data, DriftMonitorError

        mock_engine = MagicMock()
        with patch(
            "src.drift_monitor.db_reader.pd.read_sql",
            side_effect=Exception("connection refused"),
        ):
            with pytest.raises(DriftMonitorError, match="Failed to fetch reference data"):
                fetch_reference_data(engine=mock_engine)


class TestFetchCurrentData:
    """Tests for fetch_current_data with mocked DB engine."""

    def test_returns_dataframe_on_success(self):
        """Should return a DataFrame with current-window tickets."""
        from src.drift_monitor.db_reader import fetch_current_data

        mock_engine = MagicMock()
        expected_df = _make_df(CURRENT_ROWS)

        with patch("src.drift_monitor.db_reader.pd.read_sql", return_value=expected_df):
            df = fetch_current_data(engine=mock_engine, window_hours=24)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 30

    def test_raises_when_no_current_data(self):
        """Should raise DriftMonitorError when time window has no tickets."""
        from src.drift_monitor.db_reader import fetch_current_data, DriftMonitorError

        mock_engine = MagicMock()
        with patch("src.drift_monitor.db_reader.pd.read_sql", return_value=pd.DataFrame()):
            with pytest.raises(DriftMonitorError, match="No current data"):
                fetch_current_data(engine=mock_engine)

    def test_raises_on_db_error(self):
        """Should wrap DB exceptions in DriftMonitorError."""
        from src.drift_monitor.db_reader import fetch_current_data, DriftMonitorError

        mock_engine = MagicMock()
        with patch(
            "src.drift_monitor.db_reader.pd.read_sql",
            side_effect=Exception("timeout"),
        ):
            with pytest.raises(DriftMonitorError, match="Failed to fetch current data"):
                fetch_current_data(engine=mock_engine)


# ---------------------------------------------------------------------------
# Story 9.1 — generate_report tests
# ---------------------------------------------------------------------------


class TestGenerateReport:
    """Tests for generate_report function."""

    def test_generates_html_file(self, tmp_path):
        """Should call Evidently and save an HTML report to output_dir."""
        from src.drift_monitor.run_drift import generate_report

        ref_df = _make_df(REFERENCE_ROWS)
        curr_df = _make_df(CURRENT_ROWS)

        # Mock the EvidentlyAI Report object
        mock_report = MagicMock()

        with patch("src.drift_monitor.run_drift.Report", return_value=mock_report) as MockReport, \
             patch("src.drift_monitor.run_drift.DataDriftPreset"), \
             patch("src.drift_monitor.run_drift.DataQualityPreset"):
            result_path = generate_report(ref_df, curr_df, output_dir=str(tmp_path))

        # Verify report.run() and report.save_html() were called
        mock_report.run.assert_called_once()
        mock_report.save_html.assert_called_once()
        # Result path should be within tmp_path
        assert str(tmp_path) in result_path
        assert result_path.endswith(".html")

    def test_filename_contains_timestamp(self, tmp_path):
        """Report filename should contain a UTC timestamp."""
        from src.drift_monitor.run_drift import generate_report

        ref_df = _make_df(REFERENCE_ROWS)
        curr_df = _make_df(CURRENT_ROWS)

        mock_report = MagicMock()
        with patch("src.drift_monitor.run_drift.Report", return_value=mock_report), \
             patch("src.drift_monitor.run_drift.DataDriftPreset"), \
             patch("src.drift_monitor.run_drift.DataQualityPreset"):
            result_path = generate_report(ref_df, curr_df, output_dir=str(tmp_path))

        filename = os.path.basename(result_path)
        assert filename.startswith("drift_report_")
        assert filename.endswith(".html")

    def test_raises_when_no_matching_columns(self, tmp_path):
        """Should raise RuntimeError if DataFrames lack monitored columns."""
        from src.drift_monitor.run_drift import generate_report

        bad_df = pd.DataFrame({"irrelevant_col": [1, 2, 3]})

        # Patch Report to a non-None MagicMock so the guard passes
        # and the column-check logic is exercised.
        with patch("src.drift_monitor.run_drift.Report", new=MagicMock()), \
             patch("src.drift_monitor.run_drift.DataDriftPreset", new=MagicMock()), \
             patch("src.drift_monitor.run_drift.DataQualityPreset", new=MagicMock()):
            with pytest.raises(RuntimeError, match="None of the target columns"):
                generate_report(bad_df, bad_df, output_dir=str(tmp_path))

    def test_fills_nan_before_evidently(self, tmp_path):
        """NaN values in monitored columns should be filled before passing to Evidently."""
        from src.drift_monitor.run_drift import generate_report

        ref_df = _make_df(REFERENCE_ROWS)
        curr_df = _make_df(CURRENT_ROWS)
        # Introduce NaN in predicted_priority
        curr_df.loc[0, "predicted_priority"] = None

        mock_report = MagicMock()
        with patch("src.drift_monitor.run_drift.Report", return_value=mock_report), \
             patch("src.drift_monitor.run_drift.DataDriftPreset"), \
             patch("src.drift_monitor.run_drift.DataQualityPreset"):
            # Should not raise
            generate_report(ref_df, curr_df, output_dir=str(tmp_path))

        mock_report.run.assert_called_once()


# ---------------------------------------------------------------------------
# Story 9.2 — run_drift_job (S3 upload) tests
# ---------------------------------------------------------------------------


class TestRunDriftJob:
    """Tests for run_drift_job — end-to-end with mocked DB and S3."""

    # Patch upload_file at its source since it's imported inside run_drift_job
    _UPLOAD_PATCH = "src.api.utils.s3_client.upload_file"

    def _setup_patches(self, tmp_path):
        """Return a dict of patches used across multiple tests."""
        return {
            "fetch_reference": patch(
                "src.drift_monitor.run_drift.fetch_reference_data",
                return_value=_make_df(REFERENCE_ROWS),
            ),
            "fetch_current": patch(
                "src.drift_monitor.run_drift.fetch_current_data",
                return_value=_make_df(CURRENT_ROWS),
            ),
            "generate_report": patch(
                "src.drift_monitor.run_drift.generate_report",
                return_value=str(tmp_path / "drift_report_20240201_000000.html"),
            ),
            "upload_file": patch(self._UPLOAD_PATCH, return_value=True),
        }

    def test_calls_upload_with_timestamped_key(self, tmp_path):
        """run_drift_job should upload with timestamped S3 key."""
        from src.drift_monitor.run_drift import run_drift_job

        patches = self._setup_patches(tmp_path)
        with patches["fetch_reference"], patches["fetch_current"], \
             patches["generate_report"], patches["upload_file"] as mock_upload:
            run_drift_job(engine=MagicMock())

        # First call should use timestamped key under drift_reports/ prefix
        first_call_args = mock_upload.call_args_list[0]
        s3_key = first_call_args[0][1]  # positional arg: object_name
        assert s3_key.startswith("drift_reports/")
        assert s3_key.endswith(".html")

    def test_calls_upload_with_latest_key(self, tmp_path):
        """run_drift_job should also upload as 'latest_drift_report.html'."""
        from src.drift_monitor.run_drift import run_drift_job

        patches = self._setup_patches(tmp_path)
        with patches["fetch_reference"], patches["fetch_current"], \
             patches["generate_report"], patches["upload_file"] as mock_upload:
            run_drift_job(engine=MagicMock())

        # Second call should use the 'latest' alias
        second_call_args = mock_upload.call_args_list[1]
        s3_key = second_call_args[0][1]
        assert s3_key == "drift_reports/latest_drift_report.html"

    def test_returns_report_path(self, tmp_path):
        """run_drift_job should return the local file path."""
        from src.drift_monitor.run_drift import run_drift_job

        expected_path = str(tmp_path / "drift_report_20240201_000000.html")
        patches = self._setup_patches(tmp_path)
        with patches["fetch_reference"], patches["fetch_current"], \
             patch(
                 "src.drift_monitor.run_drift.generate_report",
                 return_value=expected_path,
             ), \
             patches["upload_file"]:
            result = run_drift_job(engine=MagicMock())

        assert result == expected_path

    def test_logs_warning_on_s3_failure(self, tmp_path, caplog):
        """Should log a warning when S3 upload fails, but not raise."""
        from src.drift_monitor.run_drift import run_drift_job
        import logging

        patches = self._setup_patches(tmp_path)
        with patches["fetch_reference"], patches["fetch_current"], \
             patches["generate_report"], \
             patch(self._UPLOAD_PATCH, return_value=False), \
             caplog.at_level(logging.WARNING):
            # Should not raise
            run_drift_job(engine=MagicMock())

        assert "S3 upload incomplete" in caplog.text


# ---------------------------------------------------------------------------
# Story 9.2 — Scheduler resilience test
# ---------------------------------------------------------------------------


class TestSchedulerResilience:
    """Tests for _safe_run_job — verifies exceptions don't crash the scheduler."""

    def test_safe_run_job_swallows_drift_monitor_error(self, caplog):
        """_safe_run_job should catch DriftMonitorError and log it."""
        from src.drift_monitor.run_drift import _safe_run_job
        from src.drift_monitor.db_reader import DriftMonitorError
        import logging

        with patch(
            "src.drift_monitor.run_drift.run_drift_job",
            side_effect=DriftMonitorError("DB unreachable"),
        ), caplog.at_level(logging.ERROR):
            # Should NOT raise
            _safe_run_job()

        assert "Scheduled drift job failed" in caplog.text

    def test_safe_run_job_swallows_runtime_error(self, caplog):
        """_safe_run_job should catch RuntimeError (e.g. Evidently failure) and log it."""
        from src.drift_monitor.run_drift import _safe_run_job
        import logging

        with patch(
            "src.drift_monitor.run_drift.run_drift_job",
            side_effect=RuntimeError("Evidently crash"),
        ), caplog.at_level(logging.ERROR):
            _safe_run_job()

        assert "Scheduled drift job failed" in caplog.text
