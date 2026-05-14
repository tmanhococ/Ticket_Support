# Story 10.1: Implement Graceful Degradation

As a MLOps Engineer,
I want the API to fallback to rule-based logic if the model fails,
So that the system never returns a 500 error during inference.

## Acceptance Criteria

1. **[AC1]** The `ModelService` in `src/api/services/model_service.py` is updated to catch inference exceptions.
2. **[AC2]** In case of an inference error or missing model, the system assigns a default `predicted_priority` (e.g., using a rule-based approach like searching for "urgent" or "critical" in the text to assign "high", otherwise "medium").
3. **[AC3]** The API successfully responds with a 201 status and the ticket is saved.
4. **[AC4]** A warning is logged when the fallback is triggered.

## Tasks / Subtasks

- [ ] Task 1: Update Model Service
  - [ ] 1.1 In `src/api/services/model_service.py`, implement a `rule_based_predict` fallback method.
  - [ ] 1.2 Update the `predict` method to try using the ML model first, and if an exception occurs (or model is None), log a warning and call the fallback method.
- [ ] Task 2: Unit Tests
  - [ ] 2.1 Add tests to ensure that `predict` uses the fallback logic when the model is missing or raises an error.

## Dev Notes

- Ensure that the fallback logic is deterministic and doesn't introduce any new failure points.

## Status

**Status:** ready-for-dev
