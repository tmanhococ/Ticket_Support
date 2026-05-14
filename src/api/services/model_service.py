import os
import logging

try:
    import joblib
except ImportError:
    joblib = None

try:
    import mlflow
    import mlflow.pyfunc
except ImportError:
    mlflow = None

logger = logging.getLogger(__name__)


class ModelService:
    def __init__(self):
        self.model = None
        self.model_source = None

    def load_model(self):
        """
        Load the model from MLflow Model Registry if available,
        otherwise fallback to local joblib file.
        """
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "")

        # Try loading from MLflow
        if tracking_uri and mlflow:
            try:
                mlflow.set_tracking_uri(tracking_uri)
                model_uri = "models:/ticket-triage-classifier/Production"
                logger.info(f"Attempting to load model from MLflow: {model_uri}")
                self.model = mlflow.pyfunc.load_model(model_uri)
                self.model_source = "mlflow"
                logger.info("Successfully loaded model from MLflow.")
                return
            except Exception as e:
                logger.warning(f"Failed to load model from MLflow: {e}")

        # Fallback to local file
        local_model_path = os.getenv("LOCAL_MODEL_PATH", "model.joblib")
        logger.info(f"Attempting to load local fallback model from {local_model_path}")
        if joblib and os.path.exists(local_model_path):
            try:
                self.model = joblib.load(local_model_path)
                self.model_source = "local"
                logger.info("Successfully loaded fallback local model.")
                return
            except Exception as e:
                logger.warning(f"Failed to load local model: {e}")

        logger.error("No model could be loaded. Inference will be disabled.")
        self.model = None
        self.model_source = None

    def rule_based_predict(self, texts: list[str]) -> list[str]:
        """Fallback rule-based prediction."""
        predictions = []
        for text in texts:
            text_lower = text.lower()
            if any(
                keyword in text_lower
                for keyword in ["urgent", "critical", "outage", "sicherheitsvorfall", "security"]
            ):
                predictions.append("high")
            else:
                predictions.append("medium")
        return predictions

    def predict(self, texts: list[str]) -> list[str]:
        """
        Predict the priority for a list of texts.
        Returns a list of labels (e.g., ['high', 'low']).
        """
        if self.model is None:
            logger.warning("Model is not loaded. Falling back to rule-based prediction.")
            return self.rule_based_predict(texts)

        try:
            # MLflow pyfunc model expects a pandas DataFrame, or list/array
            # Our sklearn pipeline inside mlflow handles lists
            predictions = self.model.predict(texts)
            return list(predictions)
        except Exception as e:
            logger.warning(f"Prediction failed: {e}. Falling back to rule-based prediction.")
            return self.rule_based_predict(texts)


model_service = ModelService()
