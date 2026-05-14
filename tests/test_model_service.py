from unittest.mock import patch, MagicMock
from src.api.services.model_service import ModelService
import pytest


@patch("src.api.services.model_service.mlflow")
@patch("src.api.services.model_service.os.getenv")
def test_load_model_from_mlflow(mock_getenv, mock_mlflow):
    mock_getenv.side_effect = lambda key, default="": (
        "http://fake-mlflow:5000" if key == "MLFLOW_TRACKING_URI" else default
    )

    mock_model = MagicMock()
    mock_mlflow.pyfunc.load_model.return_value = mock_model

    service = ModelService()
    service.load_model()

    mock_mlflow.set_tracking_uri.assert_called_once_with("http://fake-mlflow:5000")
    mock_mlflow.pyfunc.load_model.assert_called_once_with(
        "models:/ticket-triage-classifier/Production"
    )
    assert service.model == mock_model
    assert service.model_source == "mlflow"


@patch("src.api.services.model_service.mlflow")
@patch("src.api.services.model_service.joblib")
@patch("src.api.services.model_service.os.path.exists")
@patch("src.api.services.model_service.os.getenv")
def test_load_fallback_model(mock_getenv, mock_exists, mock_joblib, mock_mlflow):
    # Simulate missing mlflow tracking URI, so it falls back
    mock_getenv.side_effect = lambda key, default="": (
        "" if key == "MLFLOW_TRACKING_URI" else "fake_model.joblib"
    )
    mock_exists.return_value = True

    mock_model = MagicMock()
    mock_joblib.load.return_value = mock_model

    service = ModelService()
    service.load_model()

    mock_joblib.load.assert_called_once_with("fake_model.joblib")
    assert service.model == mock_model
    assert service.model_source == "local"


def test_predict_without_model_uses_fallback():
    service = ModelService()
    service.model = None
    result = service.predict(["this is an urgent issue", "just a normal question"])
    assert result == ["high", "medium"]

def test_predict_exception_uses_fallback():
    service = ModelService()
    mock_model = MagicMock()
    mock_model.predict.side_effect = Exception("Model failed")
    service.model = mock_model
    result = service.predict(["critical outage", "normal"])
    assert result == ["high", "medium"]


def test_predict_success():
    service = ModelService()
    mock_model = MagicMock()
    mock_model.predict.return_value = ["high", "low"]
    service.model = mock_model

    result = service.predict(["test ticket 1", "test ticket 2"])

    mock_model.predict.assert_called_once_with(["test ticket 1", "test ticket 2"])
    assert result == ["high", "low"]
