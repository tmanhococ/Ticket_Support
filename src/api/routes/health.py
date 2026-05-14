"""
Health-check endpoint.

GET /health → {"status": "ok", "db": "connected" | "unavailable"}

Always returns HTTP 200 — never 500 — even when DB is down.
"""

from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool

from src.api.database import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health", summary="Service liveness and DB connectivity probe")
async def health_check() -> dict:
    """
    Returns service status and DB reachability.

    - status: always "ok" (service is alive)
    - db: "connected" if PostgreSQL is reachable, "unavailable" otherwise
    """
    db_ok = await check_db_connection()
    return {
        "status": "ok",
        "db": "connected" if db_ok else "unavailable",
    }

@router.post("/predict/test", summary="Test model inference manually")
async def test_predict(request: Request, text: str) -> dict:
    """
    Test endpoint to verify model loading and inference.
    Takes a simple text string and returns the predicted label.
    """
    model_service = request.app.state.model_service
    if model_service.model is None:
        return {"error": "Model is not loaded."}
    
    try:
        predictions = await run_in_threadpool(model_service.predict, [text])
        return {
            "text": text,
            "predicted_label": predictions[0],
            "model_source": model_service.model_source
        }
    except Exception as e:
        return {"error": f"Prediction failed: {e}"}

