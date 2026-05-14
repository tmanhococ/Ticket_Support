"""
Ticket intake endpoint.

POST /tickets/  — validate payload (TicketIn) and persist to PostgreSQL.

Design rules (08_agent_workflow_rules.md §3, 04_environment_and_deployment.md §5):
- DB write failure → HTTP 503 (never 500). Mandatory try-except + rollback.
- No inference / predicted_priority here (Epic 8 — Shadow Mode).
- No S3 raw data upload here (Epic 5).
"""

from typing import Annotated
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import get_db
from src.api.models import Ticket
from src.api.schemas import TicketIn

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post(
    "/",
    status_code=201,
    summary="Ingest a support ticket",
    response_description="Ticket accepted and persisted",
)
async def create_ticket(
    request: Request,
    payload: TicketIn,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Validate and persist an incoming support ticket.

    - Returns **201** with `ticket_id` and `timestamp` on success.
    - Returns **422** automatically for invalid payloads (Pydantic).
    - Returns **503** if the DB write fails — never 500.
    """
    ticket = Ticket(
        ticket_id=payload.ticket_id,
        subject=payload.subject,
        body=payload.body,
        timestamp=payload.timestamp,
        language=payload.language,
        queue=payload.queue,
        type=payload.type,
    )

    # Shadow Inference
    try:
        model_service = request.app.state.model_service
        if model_service.model is not None:
            # Combine subject and body for text classification
            combined_text = f"{payload.subject} {payload.body}"
            # Run CPU-bound prediction in a separate thread
            predictions = await run_in_threadpool(model_service.predict, [combined_text])
            if predictions and len(predictions) > 0:
                ticket.predicted_priority = predictions[0]
    except Exception as e:
        # Graceful degradation: log the error and continue without setting predicted_priority
        logging.warning(f"Shadow inference failed for ticket {payload.ticket_id}: {e}")
    try:
        db.add(ticket)
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(status_code=503, detail="storage_unavailable") from exc

    return {
        "ticket_id": str(payload.ticket_id),
        "timestamp": payload.timestamp.isoformat(),
    }
