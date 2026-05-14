# Story 8.1: Load Model in API

As a MLOps Engineer,
I want the FastAPI app to load the registered model from MLflow,
So that it can use it for inference.

## Acceptance Criteria

1. **[AC1]** When the FastAPI server starts (lifespan event), it connects to MLflow and downloads the `Production` tagged model `ticket-triage-classifier`.
2. **[AC2]** The model is loaded into memory and made accessible to API endpoints via a FastAPI dependency or application state.
3. **[AC3]** If MLflow is unreachable or the model is not found, it gracefully falls back to loading a local fallback model (`model.joblib`), or disables prediction without crashing the API.
4. **[AC4]** A new simple `/predict/test` endpoint or a test service function is created to verify the model can successfully predict a hardcoded text string.

## Tasks / Subtasks

- [x] Task 1: Create a Model Service
  - [x] 1.1 Create `src/api/services/model_service.py`.
  - [x] 1.2 Implement a class or functions to load the model using `mlflow.pyfunc.load_model("models:/ticket-triage-classifier/Production")`.
  - [x] 1.3 Add a fallback mechanism (try/except) to load a local `model.joblib` or disable inference gracefully.
- [x] Task 2: Integrate into FastAPI lifespan
  - [x] 2.1 Update `src/api/main.py` lifespan context manager to load the model on startup.
  - [x] 2.2 Store the loaded model in `app.state.model` or inject it via a dependency.
- [x] Task 3: Unit Tests
  - [x] 3.1 Write tests mocking `mlflow` to verify model loading logic.
  - [x] 3.2 Write tests for the fallback mechanism.

## Dev Notes

- **Architecture Compliance:** Epic 8 requires Shadow Mode. This story provides the foundation by bringing the model into the API's memory.
- **Graceful Degradation:** The API must start successfully even if MLflow is down. Prediction can be skipped later if the model is `None`.
- **Note:** MLflow URI comes from `MLFLOW_TRACKING_URI` environment variable.

## File List
- `src/api/main.py`
- `src/api/services/model_service.py`
- `tests/test_model_service.py`

## Change Log
- 2026-05-14: Story created.

## Status

**Status:** done

### Review Findings

- [x] [Review][Patch] Blocking Async Route [`src/api/routes/health.py`:41] — The route `test_predict` is `async def` but calls the synchronous CPU-bound method `model_service.predict()`. This blocks the FastAPI event loop. It should be wrapped in `fastapi.concurrency.run_in_threadpool`.
