"""
Training pipeline for Ticket Triage baseline model.

Epic 6 — Story 6.1: Develop Training Pipeline
Architecture: scikit-learn TF-IDF + Logistic Regression pipeline (simple baseline).

Usage:
    python -m src.model.train --data-path <path_to_csv> --output-dir <dir>
    python -m src.model.train  # uses built-in synthetic dataset

The trained model artifact is saved as: <output_dir>/model.joblib
In Epic 7, MLflow logging will be added on top of this script.
"""

import argparse
import logging
import os
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

# ---------------------------------------------------------------------------
# MLflow Configuration (Graceful Fallback)
# ---------------------------------------------------------------------------

try:
    import mlflow
    import mlflow.sklearn

    _mlflow_available = True
except ImportError:
    _mlflow_available = False


def _log_to_mlflow(pipeline: Pipeline, params: dict, metrics: dict):
    """Log run to MLflow if available and reachable."""
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "")
    if not tracking_uri or not _mlflow_available:
        logger.info(
            "MLFLOW_TRACKING_URI not set or mlflow not installed — skipping MLflow logging."
        )
        return
    try:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("ticket-triage")
        with mlflow.start_run():
            mlflow.log_params(params)
            for k, v in metrics.items():
                mlflow.log_metric(k, v)
            mlflow.sklearn.log_model(
                pipeline,
                artifact_path="model",
                registered_model_name="ticket-triage-classifier",
            )
        logger.info("MLflow run logged successfully.")
    except Exception as exc:
        logger.warning("MLflow logging failed (non-fatal): %s", exc)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LABELS = ["low", "medium", "high"]
DEFAULT_OUTPUT_DIR = "artifacts"
DEFAULT_MODEL_FILENAME = "model.joblib"
TEXT_COLUMN = "text"
LABEL_COLUMN = "priority"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Synthetic dataset (used when no real data is provided)
# ---------------------------------------------------------------------------


def generate_synthetic_dataset() -> pd.DataFrame:
    """
    Generate a small synthetic ticket dataset for bootstrapping.

    Returns a DataFrame with columns: [text, priority].
    Each label (high/medium/low) has representative phrases so the
    TF-IDF vectoriser has something meaningful to learn from.
    """
    samples = [
        # high priority
        ("Production server is completely down, urgent fix needed", "high"),
        ("Critical security breach detected, immediate action required", "high"),
        ("Payment gateway failing, customers cannot checkout", "high"),
        ("Database corruption detected in main cluster", "high"),
        ("All users locked out of the system, urgent", "high"),
        ("API returning 500 errors for all requests, critical", "high"),
        ("Data loss incident in production environment", "high"),
        ("Service completely unavailable, impacting all customers", "high"),
        ("Urgent: SSL certificate expired, site inaccessible", "high"),
        ("Production pipeline crashed, data not processing", "high"),
        # medium priority
        ("Login page loading slowly for some users", "medium"),
        ("Report export feature not working for certain file types", "medium"),
        ("Some dashboard charts not rendering correctly", "medium"),
        ("Email notifications delayed by several hours", "medium"),
        ("Search results showing outdated information", "medium"),
        ("Mobile app crashing intermittently on Android devices", "medium"),
        ("File upload failing for files larger than 10MB", "medium"),
        ("Password reset email not arriving for some accounts", "medium"),
        ("Bulk import taking too long, performance issue", "medium"),
        ("Two-factor authentication occasionally not working", "medium"),
        # low priority
        ("Could you add a dark mode to the UI?", "low"),
        ("Request to update help documentation links", "low"),
        ("Minor typo in the about page text", "low"),
        ("Suggestion to improve button label wording", "low"),
        ("Would be nice to have CSV export on this report", "low"),
        ("Can you add keyboard shortcut for save action?", "low"),
        ("Logo looks slightly misaligned on the settings page", "low"),
        ("Please update the copyright year in the footer", "low"),
        ("Request for additional language support in UI", "low"),
        ("Suggestion to reorder columns in the ticket list view", "low"),
    ]
    df = pd.DataFrame(samples, columns=[TEXT_COLUMN, LABEL_COLUMN])
    logger.info("Generated synthetic dataset with %d samples.", len(df))
    return df


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_dataset(data_path: Optional[str]) -> pd.DataFrame:
    """
    Load ticket dataset from a CSV file or fall back to the synthetic set.

    Args:
        data_path: Path to a CSV file containing at minimum the columns
                   ``text`` and ``priority``. Pass ``None`` to use the
                   built-in synthetic dataset.

    Returns:
        DataFrame with at least ``text`` and ``priority`` columns.

    Raises:
        FileNotFoundError: If ``data_path`` is given but does not exist.
        ValueError: If required columns are missing in the CSV.
    """
    if data_path is None:
        logger.info("No data path provided — using synthetic dataset.")
        return generate_synthetic_dataset()

    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    logger.info("Loaded %d rows from %s", len(df), path)

    missing = {TEXT_COLUMN, LABEL_COLUMN} - set(df.columns)
    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {missing}. " f"Got: {list(df.columns)}"
        )

    return df


# ---------------------------------------------------------------------------
# Model building
# ---------------------------------------------------------------------------


def build_pipeline() -> Pipeline:
    """
    Build the scikit-learn training pipeline.

    Architecture (intentionally simple for the baseline):
      1. TfidfVectorizer — converts raw ticket text into TF-IDF feature matrix.
      2. LogisticRegression — multi-class classifier with 'lbfgs' solver.

    Returns:
        Unfitted sklearn Pipeline.
    """
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    max_features=5000,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


# ---------------------------------------------------------------------------
# Training entry point
# ---------------------------------------------------------------------------


def train(
    data_path: Optional[str] = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    test_size: float = 0.2,
    random_state: int = 42,
) -> str:
    """
    Train the baseline classification pipeline and save the artifact.

    Steps:
      1. Load dataset (CSV or synthetic).
      2. Split into train / test sets.
      3. Fit the TF-IDF + LogisticRegression pipeline on the training set.
      4. Evaluate on the test set and log metrics.
      5. Serialise the fitted pipeline with ``joblib`` to ``output_dir/model.joblib``.

    Args:
        data_path:    Path to CSV dataset; ``None`` → synthetic data.
        output_dir:   Directory where the model artifact will be saved.
        test_size:    Fraction of data reserved for evaluation.
        random_state: Seed for reproducible train/test split.

    Returns:
        Absolute path to the saved model artifact.
    """
    # 1. Load data
    df = load_dataset(data_path)

    X = df[TEXT_COLUMN].astype(str)
    y = df[LABEL_COLUMN].astype(str)

    # 2. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    logger.info(
        "Train/test split: %d training samples, %d test samples.",
        len(X_train),
        len(X_test),
    )

    # 3. Build & fit
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    logger.info("Model training complete.")

    # 4. Evaluate
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    report_dict = classification_report(
        y_test, y_pred, labels=LABELS, zero_division=0, output_dict=True
    )
    report_str = classification_report(y_test, y_pred, labels=LABELS, zero_division=0)
    logger.info("Test Accuracy: %.4f", acc)
    logger.info("Classification Report:\n%s", report_str)

    # 4.1 MLflow Logging
    params = {
        "test_size": test_size,
        "random_state": random_state,
        "ngram_range": pipeline.named_steps["tfidf"].ngram_range,
        "max_features": pipeline.named_steps["tfidf"].max_features,
        "max_iter": pipeline.named_steps["clf"].max_iter,
    }

    metrics = {"accuracy": float(acc)}
    for label in LABELS:
        for metric_name in ["precision", "recall", "f1-score"]:
            key = f"{label}_{metric_name.replace('-', '_')}"
            metrics[key] = float(report_dict[label][metric_name])

    _log_to_mlflow(pipeline, params, metrics)

    # 5. Save artifact
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    model_path = out_path / DEFAULT_MODEL_FILENAME
    joblib.dump(pipeline, model_path)
    logger.info("Model artifact saved to: %s", model_path.resolve())

    return str(model_path.resolve())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train baseline ticket-triage classifier (Epic 6)."
    )
    parser.add_argument(
        "--data-path",
        default=None,
        help="Path to CSV file with 'text' and 'priority' columns. "
        "Omit to use built-in synthetic dataset.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save the model artifact (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Fraction of data to use for evaluation (default: 0.2).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    saved_path = train(
        data_path=args.data_path,
        output_dir=args.output_dir,
        test_size=args.test_size,
    )
    print(f"\n✅ Model saved to: {saved_path}")
