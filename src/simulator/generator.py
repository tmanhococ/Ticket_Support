"""
src/simulator/generator.py
--------------------------
Ticket generation utilities for the Stream Simulator (Epic 2).

Public API:
    generate_ticket(seed=None)          -> dict  # always valid against TicketIn
    generate_invalid_ticket(pattern, seed) -> dict  # intentionally fails TicketIn validation
    QUEUES, TYPES, INVALID_PATTERNS     — exported constants
"""

import random
import uuid
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# English template pool (10 entries)
# ---------------------------------------------------------------------------
SUBJECTS_EN = [
    "Cannot login to the portal",
    "Account locked after multiple failed attempts",
    "Payment not processed correctly",
    "System outage affecting all users",
    "Data not syncing between devices",
    "Feature request: export to CSV",
    "Performance degradation on dashboard",
    "Security alert: unauthorized access attempt",
    "Invoice shows incorrect amount",
    "Product returns process unclear",
]

BODIES_EN = [
    "Users are unable to log in to the main portal since the last deployment. "
    "The login button becomes unresponsive after entering credentials.",
    "Our account has been locked after three failed login attempts. "
    "We need immediate access restored for the operations team.",
    "A payment of $500 was debited from our account but the system shows the order "
    "as 'Payment Pending'. Please investigate.",
    "The entire system appears to be offline for the past 30 minutes. "
    "All employees are affected and business operations have halted.",
    "Data entered on mobile devices is not appearing on the desktop application. "
    "This inconsistency is causing issues for our field team.",
    "We would like the ability to export all ticket data to CSV format for our weekly "
    "reporting. Please consider adding this feature.",
    "The analytics dashboard has become very slow to load over the past week, "
    "taking more than 2 minutes to display data.",
    "We detected an unauthorized login attempt from an unknown IP address. "
    "Please review and secure our account immediately.",
    "Our latest invoice (#INV-2024-0531) shows a charge for a service we cancelled "
    "in March. Please issue a corrected invoice.",
    "We need to return 3 items from order #ORD-9876 but the returns portal keeps "
    "showing an error when we submit the request.",
]

# ---------------------------------------------------------------------------
# German template pool (5 entries)
# ---------------------------------------------------------------------------
SUBJECTS_DE = [
    "Wesentlicher Sicherheitsvorfall",
    "Anmeldeproblem seit dem letzten Update",
    "Rechnungsfehler für Monat Mai",
    "System reagiert nicht mehr",
    "Frage zur Produktkompatibilität",
]

BODIES_DE = [
    "Sehr geehrtes Support-Team, ich möchte einen gravierenden Sicherheitsvorfall "
    "melden, der mehrere Komponenten unserer Infrastruktur betrifft. Bitte reagieren "
    "Sie umgehend.",
    "Seit dem letzten Software-Update können sich mehrere Mitarbeiter nicht mehr in "
    "das System einloggen. Bitte prüfen Sie das Problem.",
    "Unsere Rechnung vom Mai enthält Posten für Dienste, die wir bereits im April "
    "storniert haben. Bitte korrigieren Sie dies.",
    "Das gesamte System reagiert seit etwa einer Stunde nicht mehr auf Anfragen. "
    "Alle unsere Mitarbeiter sind davon betroffen.",
    "Ich benötige Informationen zur Kompatibilität Ihrer Produkte mit unserem "
    "bestehenden ERP-System. Bitte senden Sie Details.",
]

# ---------------------------------------------------------------------------
# Domain constants
# ---------------------------------------------------------------------------
QUEUES = [
    "Technical Support",
    "Customer Service",
    "Billing and Payments",
    "Product Support",
    "IT Support",
]

TYPES = ["Incident", "Request", "Problem", "Change"]

INVALID_PATTERNS = [
    "missing_subject",
    "missing_body",
    "missing_ticket_id",
    "missing_timestamp",
    "empty_subject",
    "empty_body",
    "invalid_uuid",
    "malformed_timestamp",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_base_ticket() -> dict:
    """Build a valid ticket dict using the current random state (not seeded here)."""
    language = random.choices(["en", "de"], weights=[70, 30])[0]
    if language == "en":
        idx = random.randrange(len(SUBJECTS_EN))
        subject, body = SUBJECTS_EN[idx], BODIES_EN[idx]
    else:
        idx = random.randrange(len(SUBJECTS_DE))
        subject, body = SUBJECTS_DE[idx], BODIES_DE[idx]

    return {
        "ticket_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subject": subject,
        "body": body,
        "language": language,
        "queue": random.choice(QUEUES),
        "type": random.choice(TYPES),
    }


# ---------------------------------------------------------------------------
# Public generators
# ---------------------------------------------------------------------------

def generate_ticket(seed: int | None = None) -> dict:
    """
    Generate a single **valid** support ticket as a dict.

    The returned dict always passes ``TicketIn`` Pydantic validation.

    Args:
        seed: Optional integer seed for reproducible output.  Only the
              non-UUID fields are deterministic; ``ticket_id`` uses
              ``uuid.uuid4()`` which is OS-random and cannot be seeded
              reliably across platforms.

    Returns:
        dict with keys: ticket_id, timestamp, subject, body, language,
        queue, type.
    """
    if seed is not None:
        random.seed(seed)
    return _build_base_ticket()


def generate_invalid_ticket(
    pattern: str | None = None,
    seed: int | None = None,
) -> dict:
    """
    Generate a ticket dict that **intentionally fails** ``TicketIn`` validation.

    Starts from a valid base ticket then corrupts exactly one field according
    to *pattern*.  When *pattern* is ``None`` a pattern is chosen randomly.

    Args:
        pattern: One of ``INVALID_PATTERNS``, or ``None`` for random choice.
        seed:    Optional integer seed for reproducible output.

    Returns:
        dict that raises ``pydantic.ValidationError`` when passed to
        ``TicketIn(**result)``.

    Raises:
        ValueError: If *pattern* is not in ``INVALID_PATTERNS``.
    """
    if seed is not None:
        random.seed(seed)

    ticket = _build_base_ticket()
    chosen = pattern if pattern is not None else random.choice(INVALID_PATTERNS)

    if chosen == "missing_subject":
        del ticket["subject"]
    elif chosen == "missing_body":
        del ticket["body"]
    elif chosen == "missing_ticket_id":
        del ticket["ticket_id"]
    elif chosen == "missing_timestamp":
        del ticket["timestamp"]
    elif chosen == "empty_subject":
        ticket["subject"] = ""
    elif chosen == "empty_body":
        ticket["body"] = ""
    elif chosen == "invalid_uuid":
        ticket["ticket_id"] = "not-a-valid-uuid"
    elif chosen == "malformed_timestamp":
        ticket["timestamp"] = "2024-13-99T99:99:99"
    else:
        raise ValueError(
            f"Unknown invalid pattern: {chosen!r}. "
            f"Must be one of: {INVALID_PATTERNS}"
        )

    return ticket


def generate_drift_ticket(seed: int | None = None) -> dict:
    """
    Generate a ticket with **biased distribution** to simulate Data Drift.

    Bias applied (vs. normal distribution):
    - Language: 80% German (de) vs. normally 30%
    - Type:     70% Incident vs. normally ~25%
    - Queue:    70% Technical Support vs. normally ~20%

    The returned dict always passes ``TicketIn`` Pydantic validation.

    Args:
        seed: Optional integer seed for reproducible output.

    Returns:
        dict with the same keys as ``generate_ticket()`` but biased distribution.
    """
    if seed is not None:
        random.seed(seed)

    language = random.choices(["en", "de"], weights=[20, 80])[0]
    if language == "en":
        idx = random.randrange(len(SUBJECTS_EN))
        subject, body = SUBJECTS_EN[idx], BODIES_EN[idx]
    else:
        idx = random.randrange(len(SUBJECTS_DE))
        subject, body = SUBJECTS_DE[idx], BODIES_DE[idx]

    return {
        "ticket_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subject": subject,
        "body": body,
        "language": language,
        # Technical Support = 70%, rest split evenly
        "queue": random.choices(QUEUES, weights=[70, 10, 10, 5, 5])[0],
        # Incident = 70%, Request = 10%, Problem = 15%, Change = 5%
        "type": random.choices(TYPES, weights=[70, 10, 15, 5])[0],
    }
