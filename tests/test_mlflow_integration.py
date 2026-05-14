"""
Tests for MLflow integration in the training pipeline — Story 7.2.
"""

from pathlib import Path
from unittest.mock import Mock, patch

from src.model.train import train


@patch("src.model.train.mlflow")
def test_mlflow_logs_called_when_uri_set(mock_mlflow, tmp_path, monkeypatch):
    """
    When MLFLOW_TRACKING_URI is set, train() should call mlflow logging methods.
    """
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://fake-mlflow:5000")

    # Mock the context manager for start_run
    mock_run = Mock()
    mock_mlflow.start_run.return_value.__enter__ = Mock(return_value=mock_run)
    mock_mlflow.start_run.return_value.__exit__ = Mock(return_value=False)

    output_dir = tmp_path / "artifacts"

    # Run training
    train(data_path=None, output_dir=str(output_dir))

    # Verify MLflow setup
    mock_mlflow.set_tracking_uri.assert_called_once_with("http://fake-mlflow:5000")
    mock_mlflow.set_experiment.assert_called_once_with("ticket-triage")
    mock_mlflow.start_run.assert_called_once()

    # Verify logging
    mock_mlflow.log_params.assert_called_once()

    # Check that log_metric was called multiple times (accuracy + 3 metrics * 3 labels = 10 times)
    assert mock_mlflow.log_metric.call_count >= 10

    # Check that log_model was called
    mock_mlflow.sklearn.log_model.assert_called_once()
    kwargs = mock_mlflow.sklearn.log_model.call_args.kwargs
    assert kwargs.get("artifact_path") == "model"
    assert kwargs.get("registered_model_name") == "ticket-triage-classifier"


@patch("src.model.train.mlflow")
def test_mlflow_fallback_when_exception_raised(mock_mlflow, tmp_path, monkeypatch):
    """
    If MLflow raises an exception during logging, training should NOT crash
    and the local artifact should still be saved.
    """
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://fake-mlflow:5000")

    # Make MLflow raise an exception when setting tracking URI
    mock_mlflow.set_tracking_uri.side_effect = Exception("MLflow server unreachable")

    output_dir = tmp_path / "artifacts"

    # Run training - should not raise exception
    saved_path = train(data_path=None, output_dir=str(output_dir))

    # Local artifact should still exist
    assert Path(saved_path).exists()
    assert saved_path.endswith("model.joblib")


@patch("src.model.train.mlflow")
def test_mlflow_not_called_when_uri_empty(mock_mlflow, tmp_path, monkeypatch):
    """
    When MLFLOW_TRACKING_URI is empty/not set, MLflow should not be called at all.
    """
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)

    output_dir = tmp_path / "artifacts"

    # Run training
    saved_path = train(data_path=None, output_dir=str(output_dir))

    # Verify MLflow was NOT called
    mock_mlflow.set_tracking_uri.assert_not_called()
    mock_mlflow.start_run.assert_not_called()
    mock_mlflow.log_params.assert_not_called()

    # Local artifact should still exist
    assert Path(saved_path).exists()
