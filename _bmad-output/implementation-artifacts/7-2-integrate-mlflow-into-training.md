# Story 7.2: Integrate MLflow into Training

As a Data Scientist,
I want the training script to log metrics and register the model to MLflow,
So that I can compare experiment versions and promote the best model to the Model Registry for use by the API.

## Acceptance Criteria

1. **[AC1]** When the training script runs (`python -m src.model.train`), it creates an MLflow run and logs training metadata (accuracy, parameters).
2. **[AC2]** The following are logged to MLflow per run:
   - **Parameters:** `test_size`, `random_state`, `ngram_range`, `max_features`, `max_iter`
   - **Metrics:** `accuracy` (float), and per-class precision/recall/f1 for `high`, `medium`, `low`
3. **[AC3]** The trained sklearn pipeline is logged as an MLflow artifact using `mlflow.sklearn.log_model()` and registered in the **Model Registry** under the name `ticket-triage-classifier`.
4. **[AC4]** The script gracefully falls back to local-only mode (joblib save only) if `MLFLOW_TRACKING_URI` is not set or the MLflow server is unreachable — without crashing.
5. **[AC5]** The MLflow tracking URI is read from the `MLFLOW_TRACKING_URI` environment variable (no hardcoded URIs in code).

## Tasks / Subtasks

- [x] Task 1: Add MLflow dependency
  - [x] 1.1 Add `mlflow==2.13.0` to `requirements.txt` (if not already added in Story 7.1).
- [x] Task 2: Integrate MLflow logging into `src/model/train.py`
  - [x] 2.1 At the start of `train()`, call `mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", ""))` and `mlflow.set_experiment("ticket-triage")`.
  - [x] 2.2 Wrap the training block in `with mlflow.start_run() as run:`.
  - [x] 2.3 Log parameters: `mlflow.log_params({...})` — test_size, random_state, tfidf ngram_range, max_features, clf max_iter.
  - [x] 2.4 Log metrics: `mlflow.log_metric("accuracy", acc)` and per-class f1/precision/recall extracted from `classification_report(..., output_dict=True)`.
  - [x] 2.5 Log and register the model: `mlflow.sklearn.log_model(pipeline, artifact_path="model", registered_model_name="ticket-triage-classifier")`.
  - [x] 2.6 Wrap MLflow calls in `try/except Exception` — if MLflow is unavailable, log a warning and continue (joblib fallback must still execute).
- [x] Task 3: Add unit tests
  - [x] 3.1 Mock `mlflow` using `unittest.mock.patch` to test that `log_params`, `log_metric`, and `log_model` are called with correct arguments when `MLFLOW_TRACKING_URI` is set.
  - [x] 3.2 Write a test that verifies the script still saves the local `model.joblib` artifact even when MLflow raises an exception (fallback mode).
  - [x] 3.3 Write a test that verifies no MLflow calls are made when `MLFLOW_TRACKING_URI` is empty/not set (local-only mode).

## Dev Notes

- **Business Context:** This story closes the loop on Model Versioning. After this story, every training run creates a versioned, queryable experiment in MLflow. This enables Epic 8 (Shadow Inference) to query the Registry for the latest `Production`-tagged model and load it into the FastAPI service.
- **Architecture Compliance:** Section 2.4: "MLflow — tracking thí nghiệm (experiments), quản lý model version". Section 3: "FastAPI Service: kéo model từ MLflow/S3". Section 4: "Model Rollback: đổi tag model ổn định trước đó trong MLflow thành Production".
- **Depends On:** Story 7.1 must be complete (MLflow server running) for end-to-end integration to work. However, unit tests in this story use mocks and do NOT require the server.

### Critical Implementation Details

**`train()` function signature must NOT change** — it is already tested by 19 tests in `tests/test_train.py`. The MLflow integration must be additive only.

**Fallback pattern (REQUIRED by architecture rule §4 Graceful Degradation):**
```python
try:
    import mlflow
    import mlflow.sklearn
    _mlflow_available = True
except ImportError:
    _mlflow_available = False

def _log_to_mlflow(pipeline, params, metrics):
    """Log run to MLflow if available and reachable."""
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "")
    if not tracking_uri or not _mlflow_available:
        logger.info("MLFLOW_TRACKING_URI not set — skipping MLflow logging.")
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
```

**Extract per-class metrics from sklearn report:**
```python
report_dict = classification_report(
    y_test, y_pred, labels=LABELS, zero_division=0, output_dict=True
)
metrics = {"accuracy": acc}
for label in LABELS:
    for metric_name in ["precision", "recall", "f1-score"]:
        key = f"{label}_{metric_name.replace('-', '_')}"
        metrics[key] = report_dict[label][metric_name]
```

**MLflow Model Registry note:** `registered_model_name` in `log_model()` auto-creates the registry entry. The first version will be tagged `None` (no stage). In Epic 8, the FastAPI service will query using:
```python
mlflow.pyfunc.load_model("models:/ticket-triage-classifier/Production")
```
For this story, just register it — no stage transitions needed yet.

- **Previous story learnings (6.1):**
  - `src/model/train.py` already exists with `train()`, `load_dataset()`, `build_pipeline()`, `generate_synthetic_dataset()`.
  - `LABELS = ["low", "medium", "high"]`, `TEXT_COLUMN = "text"`, `LABEL_COLUMN = "priority"` are defined as module constants — reuse them.
  - The `train()` function returns the local artifact path (str) — keep this return value unchanged.
  - Tests in `tests/test_train.py` must remain 100% green after this story's changes.
  - Pattern used: `joblib.dump(pipeline, model_path)` for local artifact — keep this as the primary save, MLflow is additive.

- **Test isolation pattern** (to avoid real network calls in tests):
  ```python
  @patch("src.model.train.mlflow")
  def test_mlflow_logs_called(mock_mlflow, tmp_path, monkeypatch):
      monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://fake-mlflow:5001")
      mock_mlflow.start_run.return_value.__enter__ = Mock(return_value=Mock())
      mock_mlflow.start_run.return_value.__exit__ = Mock(return_value=False)
      train(data_path=None, output_dir=str(tmp_path))
      mock_mlflow.log_params.assert_called_once()
  ```

## Dev Agent Record
- **Debug Log:** Successfully executed tests. 22 passing tests out of 22 for train and mlflow integration modules.
- **Completion Notes:**
  - ✅ AC1: Training metadata is logged into MLflow.
  - ✅ AC2: Added extraction of per-class f1, recall and precision metrics and model parameters.
  - ✅ AC3: Logged the model using `mlflow.sklearn.log_model` and registered it as `ticket-triage-classifier`.
  - ✅ AC4: Used `try/except` for graceful fallback. Missing `MLFLOW_TRACKING_URI` or `mlflow` package causes it to skip and just save the joblib artifact locally.
  - ✅ AC5: MLflow tracking URI is read from `os.getenv`.

## File List
- `src/model/train.py`
- `tests/test_mlflow_integration.py`

## Change Log
- 2026-05-14: Story created.
- 2026-05-14: Implemented MLflow integration in `train.py` with fallback mechanisms and unit tests.

## Status

**Status:** review
