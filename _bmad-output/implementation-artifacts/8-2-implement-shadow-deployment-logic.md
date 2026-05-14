# Story 8.2: Implement Shadow Deployment Logic

As a MLOps Engineer,
I want the API to run predictions but not alter the external behavior yet,
So that I can test the model safely on production traffic.

## Acceptance Criteria

1. **[AC1]** The `Ticket` database model is updated to include a `predicted_priority` column (nullable string).
2. **[AC2]** When a ticket hits `POST /tickets/`, the API asynchronously or synchronously calls the loaded model to predict the label (`high`, `medium`, `low`).
3. **[AC3]** The `predicted_priority` is saved to the database along with the rest of the ticket data.
4. **[AC4]** The API response (JSON) remains exactly the same as before (does NOT return the predicted priority to the client).
5. **[AC5]** If the model is not loaded (due to MLflow/fallback failure) or throws an error during inference, the API catches the error, leaves `predicted_priority` as null, and successfully saves the ticket and returns 201 (Graceful Degradation).

## Tasks / Subtasks

- [x] Task 1: Update Database Schema
  - [x] 1.1 Add `predicted_priority: Mapped[str | None] = mapped_column(String(50), nullable=True)` to `Ticket` in `src/api/models.py`.
- [x] Task 2: Update Intake Endpoint
  - [x] 2.1 In `src/api/routes/tickets.py`, retrieve the loaded model from `app.state` or dependencies.
  - [x] 2.2 Call the model's predict method using the ticket's `subject` + `body` (or whatever format the pipeline expects).
  - [x] 2.3 Assign the prediction to `ticket.predicted_priority` before `db.commit()`.
- [x] Task 3: Error Handling
  - [x] 3.1 Wrap the prediction logic in a `try/except` block to ensure prediction failures don't block the ticket creation.
- [x] Task 4: Unit Tests
  - [x] 4.1 Update API tests to verify that `predicted_priority` is saved when a mocked model returns a result.
  - [x] 4.2 Add test to ensure API still returns 201 when the mock model raises an Exception.

## Dev Notes

- **Shadow Mode:** This is the core of Epic 8. We are predicting on live traffic but hiding it from the user.
- **Integration:** The model expects a list of strings or pandas DataFrame. Ensure the input format matches the pipeline trained in Epic 6/7. E.g., `model.predict([f"{payload.subject} {payload.body}"])`.

## File List
- `src/api/models.py`
- `src/api/routes/tickets.py`
- `tests/test_api_tickets.py`

## Change Log
- 2026-05-14: Story created.

## Status

**Status:** done

### Review Findings

- [x] [Review][Patch] Blocking Async Route [`src/api/routes/tickets.py`:59] — The route `create_ticket` is `async def` but calls the synchronous CPU-bound method `model_service.predict()`. This blocks the FastAPI event loop during inference. It should be wrapped in `fastapi.concurrency.run_in_threadpool`.
