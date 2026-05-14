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

    def predict(self, texts: list[str]) -> list[str]:
        """
        Predict the priority for a list of texts.
        Returns a list of labels (e.g., ['high', 'low']).
        """
        if self.model is None:
            raise ValueError("Model is not loaded.")

        try:
            # MLflow pyfunc model expects a pandas DataFrame, or list/array
            # Our sklearn pipeline inside mlflow handles lists
            predictions = self.model.predict(texts)
            return list(predictions)
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise


model_service = ModelService()
