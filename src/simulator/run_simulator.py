"""
src/simulator/run_simulator.py
------------------------------
Stream Simulator entrypoint for the Ticket Triage MLOps project (Epic 2, Story 2.2).

Usage examples:
    # Normal mode — 10 tickets at 2 req/s
    python -m src.simulator.run_simulator --url http://localhost:8000 --rate 2 --total 10

    # Drift mode — infinite, 1 req/s
    python -m src.simulator.run_simulator --url http://localhost:8000 --drift

    # Mixed mode — 20% invalid payloads to test rejection pipeline
    python -m src.simulator.run_simulator --rate 2 --total 50 --invalid-rate 0.2

    # Drift + invalid mix
    python -m src.simulator.run_simulator --drift --invalid-rate 0.15

Stop with CTRL+C — prints ingestion funnel summary before exiting.
"""

import argparse
import logging
import random
import time
from dataclasses import dataclass

import httpx

from src.simulator.generator import (
    generate_drift_ticket,
    generate_invalid_ticket,
    generate_ticket,
)

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Counters dataclass for ingestion funnel tracking
# ---------------------------------------------------------------------------

@dataclass
class Counters:
    """Track per-status counts for the ingestion funnel summary."""

    total: int = 0
    accepted: int = 0      # HTTP 201 — ticket saved to DB
    rejected_422: int = 0  # HTTP 422 — Pydantic validation failure (expected for invalids)
    errors: int = 0        # Other 4xx, 5xx, connection errors

    def summary(self) -> str:
        return (
            f"Total={self.total} | "
            f"Accepted=201:{self.accepted} | "
            f"Rejected=422:{self.rejected_422} | "
            f"Errors:{self.errors}"
        )


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the simulator."""
    parser = argparse.ArgumentParser(
        description="Ticket Stream Simulator — sends tickets to the FastAPI intake endpoint.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the FastAPI service (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=1.0,
        help="Requests per second (default: 1.0)",
    )
    parser.add_argument(
        "--total",
        type=int,
        default=0,
        help="Total number of requests to send; 0 = infinite (default: 0)",
    )
    parser.add_argument(
        "--drift",
        action="store_true",
        default=False,
        help="Enable drift mode — biases language/type/queue distribution",
    )
    parser.add_argument(
        "--invalid-rate",
        type=float,
        default=0.0,
        dest="invalid_rate",
        metavar="RATE",
        help=(
            "Fraction of requests that send intentionally invalid payloads "
            "(0.0–1.0, default: 0.0). These are expected to return HTTP 422."
        ),
    )
    args = parser.parse_args()
    if not 0.0 <= args.invalid_rate <= 1.0:
        parser.error("--invalid-rate must be between 0.0 and 1.0")
    if args.rate <= 0:
        parser.error("--rate must be greater than 0")
    return args


# ---------------------------------------------------------------------------
# HTTP sender with retry logic
# ---------------------------------------------------------------------------

def send_ticket(
    url: str,
    payload: dict,
    is_invalid: bool = False,
    retries: int = 3,
) -> int:
    """
    POST a ticket payload to the API.

    Args:
        url:        Base URL of the FastAPI service.
        payload:    Ticket dict to send as JSON body.
        is_invalid: When True, the payload is intentionally malformed.
                    Invalid tickets are NEVER retried (422 is the expected outcome).
        retries:    Max retry attempts on 5xx / connection errors (for valid tickets).

    Returns:
        Final HTTP status code, or -1 on max retries exceeded.
    """
    target = f"{url}/tickets/"
    max_attempts = 1 if is_invalid else retries
    ticket_id = payload.get("ticket_id", "<missing>")

    for attempt in range(1, max_attempts + 1):
        try:
            response = httpx.post(target, json=payload, timeout=10.0)
            status = response.status_code

            if status == 201:
                logger.info("[SUCCESS] ticket_id=%s status=201", ticket_id)
                return status

            elif status == 422:
                if is_invalid:
                    logger.info(
                        "[INVALID_SENT] ticket_id=%s status=422 — expected rejection",
                        ticket_id,
                    )
                else:
                    logger.warning(
                        "[VALIDATION_ERROR] ticket_id=%s status=422 — unexpected (valid payload rejected)",
                        ticket_id,
                    )
                return status

            elif 400 <= status < 500:
                logger.warning(
                    "[CLIENT_ERROR] ticket_id=%s status=%d", ticket_id, status
                )
                return status

            else:  # 5xx
                logger.warning(
                    "[SERVER_ERROR] ticket_id=%s status=%d attempt=%d/%d",
                    ticket_id,
                    status,
                    attempt,
                    max_attempts,
                )
                if attempt < max_attempts:
                    time.sleep(2)

        except httpx.RequestError as exc:
            logger.warning(
                "[CONNECT_ERROR] ticket_id=%s attempt=%d/%d error=%s",
                ticket_id,
                attempt,
                max_attempts,
                exc,
            )
            if attempt < max_attempts:
                time.sleep(2)

    logger.warning("[MAX_RETRIES] ticket_id=%s — skipping", ticket_id)
    return -1


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace) -> None:
    """Run the simulator loop until `--total` is reached or CTRL+C."""
    mode = "DRIFT" if args.drift else "NORMAL"
    base_generator = generate_drift_ticket if args.drift else generate_ticket

    logger.info(
        "Starting simulator | mode=%s invalid_rate=%.0f%% url=%s rate=%.1f req/s total=%s",
        mode,
        args.invalid_rate * 100,
        args.url,
        args.rate,
        args.total if args.total > 0 else "∞",
    )

    counters = Counters()
    interval = 1.0 / args.rate

    try:
        while True:
            # Decide: valid or intentionally invalid request?
            is_invalid = random.random() < args.invalid_rate
            payload = generate_invalid_ticket() if is_invalid else base_generator()

            status = send_ticket(args.url, payload, is_invalid=is_invalid)
            counters.total += 1

            if status == 201:
                counters.accepted += 1
            elif status == 422:
                counters.rejected_422 += 1
            else:
                counters.errors += 1

            if args.total > 0 and counters.total >= args.total:
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        pass  # Clean exit — summary printed below

    logger.info("Simulator stopped. %s", counters.summary())


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run(parse_args())
