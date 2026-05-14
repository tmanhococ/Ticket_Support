"""
Unit tests for src/model/train.py — Story 6.1: Develop Training Pipeline.

Test coverage:
  - Synthetic dataset generation (shape, columns, label distribution)
  - load_dataset() with and without a real CSV path
  - build_pipeline() returns a valid sklearn Pipeline
  - train() produces a model that predicts valid labels
  - train() saves a model artifact (joblib file) to disk
  - Trained model can be re-loaded and used for inference
  - Error handling for missing files and missing columns
"""

import os
import tempfile
from pathlib import Path

import joblib
import pandas as pd
import pytest

from src.model.train import (
    DEFAULT_MODEL_FILENAME,
    LABEL_COLUMN,
    LABELS,
    TEXT_COLUMN,
    build_pipeline,
    generate_synthetic_dataset,
    load_dataset,
    train,
)


# ---------------------------------------------------------------------------
# generate_synthetic_dataset
# ---------------------------------------------------------------------------


class TestGenerateSyntheticDataset:
    """Tests for the built-in synthetic dataset factory."""

    def test_returns_dataframe(self):
        df = generate_synthetic_dataset()
        assert isinstance(df, pd.DataFrame)

    def test_has_required_columns(self):
        df = generate_synthetic_dataset()
        assert TEXT_COLUMN in df.columns
        assert LABEL_COLUMN in df.columns

    def test_has_all_three_labels(self):
        df = generate_synthetic_dataset()
        unique_labels = set(df[LABEL_COLUMN].unique())
        assert unique_labels == {"low", "medium", "high"}

    def test_no_empty_text(self):
        df = generate_synthetic_dataset()
        assert df[TEXT_COLUMN].str.strip().ne("").all(), "Some text entries are empty"

    def test_minimum_samples_per_label(self):
        """At least 3 samples per label to allow train/test split."""
        df = generate_synthetic_dataset()
        counts = df[LABEL_COLUMN].value_counts()
        for label in LABELS:
            assert counts.get(label, 0) >= 3, (
                f"Label '{label}' has fewer than 3 samples: {counts.get(label, 0)}"
            )


# ---------------------------------------------------------------------------
# load_dataset
# ---------------------------------------------------------------------------


class TestLoadDataset:
    """Tests for data loading logic."""

    def test_none_returns_synthetic(self):
        df = load_dataset(None)
        assert isinstance(df, pd.DataFrame)
        assert TEXT_COLUMN in df.columns

    def test_loads_valid_csv(self, tmp_path):
        csv_path = tmp_path / "tickets.csv"
        data = pd.DataFrame(
            {
                TEXT_COLUMN: ["server down", "update logo", "slow login"],
                LABEL_COLUMN: ["high", "low", "medium"],
            }
        )
        data.to_csv(csv_path, index=False)
        df = load_dataset(str(csv_path))
        assert len(df) == 3
        assert set(df.columns) >= {TEXT_COLUMN, LABEL_COLUMN}

    def test_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="Dataset not found"):
            load_dataset("/nonexistent/path/data.csv")

    def test_raises_value_error_missing_columns(self, tmp_path):
        csv_path = tmp_path / "bad.csv"
        pd.DataFrame({"description": ["ticket 1"], "level": ["high"]}).to_csv(
            csv_path, index=False
        )
        with pytest.raises(ValueError, match="missing required columns"):
            load_dataset(str(csv_path))


# ---------------------------------------------------------------------------
# build_pipeline
# ---------------------------------------------------------------------------


class TestBuildPipeline:
    """Tests for the sklearn Pipeline factory."""

    def test_returns_pipeline(self):
        from sklearn.pipeline import Pipeline

        pipe = build_pipeline()
        assert isinstance(pipe, Pipeline)

    def test_pipeline_has_tfidf_and_clf_steps(self):
        pipe = build_pipeline()
        step_names = [name for name, _ in pipe.steps]
        assert "tfidf" in step_names
        assert "clf" in step_names

    def test_pipeline_is_unfitted(self):
        """Calling predict on an unfitted pipeline should raise NotFittedError."""
        from sklearn.exceptions import NotFittedError

        pipe = build_pipeline()
        with pytest.raises(NotFittedError):
            pipe.predict(["some ticket text"])


# ---------------------------------------------------------------------------
# train() — end-to-end
# ---------------------------------------------------------------------------


class TestTrain:
    """End-to-end tests for the train() function."""

    def test_train_creates_model_file(self, tmp_path):
        output_dir = str(tmp_path / "artifacts")
        saved = train(data_path=None, output_dir=output_dir)
        assert Path(saved).exists(), f"Expected model file at {saved}"
        assert saved.endswith(DEFAULT_MODEL_FILENAME)

    def test_train_returns_absolute_path(self, tmp_path):
        saved = train(data_path=None, output_dir=str(tmp_path))
        assert Path(saved).is_absolute()

    def test_saved_model_is_loadable(self, tmp_path):
        saved = train(data_path=None, output_dir=str(tmp_path))
        model = joblib.load(saved)
        assert model is not None

    def test_loaded_model_predicts_valid_labels(self, tmp_path):
        saved = train(data_path=None, output_dir=str(tmp_path))
        model = joblib.load(saved)
        test_texts = [
            "production server is down urgently",
            "login is a bit slow sometimes",
            "please update the help page text",
        ]
        predictions = model.predict(test_texts)
        assert len(predictions) == len(test_texts)
        for pred in predictions:
            assert pred in LABELS, f"Unexpected label: {pred}"

    def test_train_with_custom_csv(self, tmp_path):
        """train() should work with a user-provided CSV dataset."""
        csv_path = tmp_path / "data.csv"
        # Need enough samples per class for stratified split
        samples = []
        for label, text_tmpl in [
            ("high", "critical production failure {}"),
            ("medium", "moderate issue with feature {}"),
            ("low", "minor cosmetic request {}"),
        ]:
            for i in range(5):
                samples.append({TEXT_COLUMN: text_tmpl.format(i), LABEL_COLUMN: label})
        pd.DataFrame(samples).to_csv(csv_path, index=False)

        saved = train(data_path=str(csv_path), output_dir=str(tmp_path / "out"))
        assert Path(saved).exists()

    def test_train_creates_output_dir_if_missing(self, tmp_path):
        output_dir = str(tmp_path / "nested" / "artifacts")
        assert not Path(output_dir).exists()
        train(data_path=None, output_dir=output_dir)
        assert Path(output_dir).exists()

    def test_model_accuracy_reasonable(self, tmp_path):
        """
        On the synthetic dataset the model should achieve at least 50% accuracy.
        This guards against accidental complete breakage of the training logic.
        """
        saved = train(data_path=None, output_dir=str(tmp_path), test_size=0.3)
        model = joblib.load(saved)
        from src.model.train import generate_synthetic_dataset

        df = generate_synthetic_dataset()
        preds = model.predict(df[TEXT_COLUMN])
        acc = (preds == df[LABEL_COLUMN]).mean()
        assert acc >= 0.5, f"Model accuracy {acc:.2f} is below minimum threshold 0.50"
