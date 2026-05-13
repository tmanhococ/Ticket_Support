"""
Pydantic schemas for Ticket Triage API.

Data Contract source: docs/project-context/02_domain_and_data_contract.md
- TicketIn  → validates incoming ticket payloads (intake endpoint)
- TicketOut → inference response shape (used from Story 1.3 / Epic 8 onwards)
"""
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TicketIn(BaseModel):
    """
    Incoming ticket payload.

    Enforces the domain Data Contract (02_domain_and_data_contract.md §2 & §6):
    - ticket_id: must be a valid UUID
    - subject / body: must not be empty (whitespace-only is also rejected)
    - timestamp: must be a valid ISO8601 datetime
    - language, queue, type: optional descriptive metadata
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    ticket_id: UUID
    timestamp: datetime
    subject: str = Field(..., max_length=500)
    body: str
    language: Optional[str] = Field(None, max_length=10)
    queue: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=50)

    @field_validator("subject", "body")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        """Reject fields that are empty after whitespace stripping."""
        if not v:
            raise ValueError("must not be empty")
        return v


class TicketOut(BaseModel):
    """
    Inference response payload.

    Data Contract source: 02_domain_and_data_contract.md §3.
    PLACEHOLDER — fully wired in Story 1.3 (endpoint) and Epic 8 (shadow inference).

    confidence_score: probability of the top predicted class (0.0–1.0).
    Works for both sklearn (.predict_proba()) and DL models (softmax output).
    Values below a threshold (e.g. 0.60) should trigger manual_review fallback.
    """

    model_config = ConfigDict(protected_namespaces=())

    ticket_id: UUID
    predicted_priority: Literal["low", "medium", "high"]
    confidence_score: float
    model_version: str
