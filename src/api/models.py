"""
SQLAlchemy ORM models for Ticket Triage API.

Table: tickets
Source: 02_domain_and_data_contract.md §2 + Story 1.3 AC3.

IMPORTANT: This module must NOT import from database.py (one-way dependency).
database.py imports Base from here — not the other way around.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


class Ticket(Base):
    """
    Persisted ticket record.

    Columns match the Data Contract (02_domain_and_data_contract.md §2).
    received_at is server-generated — not supplied by the client.
    """

    __tablename__ = "tickets"

    ticket_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True
    )
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    queue: Mapped[str | None] = mapped_column(String(100), nullable=True)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
