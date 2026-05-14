# Story 6.1: Develop Training Pipeline

As a Data Scientist,
I want a script to train a text classification model,
So that the system can automatically categorize tickets.

## Acceptance Criteria

1. **[AC1]** A Python training script (`src/model/train.py`) is created to train a baseline text classification model (TF-IDF + Logistic Regression sklearn pipeline).
2. **[AC2]** The script can load a dataset of historical tickets (mocked or real) from a specified path.
3. **[AC3]** The model is trained to classify text into `high`, `medium`, or `low` priorities.
4. **[AC4]** The trained model artifact (`.joblib` file) is saved locally for future use.

## Tasks / Subtasks

- [x] Task 1: Setup Model Training Environment
  - [x] 1.1 Add required ML dependencies (`scikit-learn==1.4.2`, `joblib==1.4.0`) to `requirements.txt`.
  - [x] 1.2 Create `src/model/train.py` script.
- [x] Task 2: Implement Training Logic
  - [x] 2.1 Implement data loading and preprocessing (TF-IDF vectorization with bigrams, sublinear TF scaling).
  - [x] 2.2 Define and train a simple baseline classification model (LogisticRegression with `class_weight="balanced"`).
  - [x] 2.3 Add evaluation metrics (accuracy_score, classification_report) printed via logger.
- [x] Task 3: Save Model Artifact
  - [x] 3.1 Implement logic to serialize and save the trained model to `artifacts/model.joblib` using `joblib.dump()`.

## Dev Notes

- **Business Context:** This is the core intelligence of the Ticket Triage system. We are starting with a simple baseline model to ensure the pipeline works end-to-end before iterating on more complex architectures.
- **Architecture Compliance:** Aligns with section 3 (System Components & Data Flow) where the model is a baseline classification model. The artifact will later be loaded by the FastAPI service. Kept simple (scikit-learn).
- **Next Steps:** In Epic 7, we will integrate MLflow into this script to track metrics and register the model. For now, just save it locally.
- **Design Decisions:**
  - Used `joblib` over `pickle` for safer/faster sklearn serialization.
  - `generate_synthetic_dataset()` provides 30 labeled samples (10 per class) as a built-in bootstrap dataset, removing the need for external data to run the pipeline.
  - `TfidfVectorizer(ngram_range=(1,2), max_features=5000, sublinear_tf=True)` captures bigrams (e.g., "server down") which are discriminative for priority classification.
  - `class_weight="balanced"` prevents bias toward any single label if class distribution is uneven.
  - `train_test_split(..., stratify=y)` ensures each split keeps the same class ratio.

## Dev Agent Record
- **Debug Log:** All 19 new tests passed on first run. No issues encountered.
- **Completion Notes:**
  - ✅ AC1: `src/model/train.py` created with TF-IDF + LogisticRegression pipeline.
  - ✅ AC2: `load_dataset()` supports CSV path or built-in synthetic dataset fallback. Validates required columns. Raises `FileNotFoundError` / `ValueError` for invalid inputs.
  - ✅ AC3: Model classifies text into `high`, `medium`, `low`. Verified by test `test_loaded_model_predicts_valid_labels`.
  - ✅ AC4: `joblib.dump()` saves artifact to configurable `output_dir/model.joblib`. Directory auto-created if missing.
  - 19 new unit tests added, 0 regressions across the full 76-test suite.

## File List

- `requirements.txt` — added `scikit-learn==1.4.2`, `joblib==1.4.0`
- `src/model/__init__.py` — new (package init)
- `src/model/train.py` — new (training pipeline)
- `tests/test_train.py` — new (19 unit tests)

## Change Log
- 2026-05-14: Story 6.1 implemented. Added scikit-learn/joblib, created training pipeline with synthetic dataset, evaluation, artifact saving. 19 unit tests — all pass. 76 total tests — all pass, zero regressions.

## Status

**Status:** review
