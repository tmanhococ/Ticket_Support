import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import AsyncSessionLocal, engine
from src.api.models import Ticket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CSV_PATH = Path("data/original/tickets.csv")

async def seed_data():
    """
    Reads data/original/tickets.csv and bulk inserts into the tickets table.
    Sets received_at back in time to simulate historical data.
    """
    if not CSV_PATH.exists():
        logger.error(f"Cannot find CSV file at {CSV_PATH.resolve()}")
        return

    logger.info(f"Loading data from {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    
    # We only care about columns that match our schema
    expected_cols = ["subject", "body", "type", "queue", "language", "priority"]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        logger.error(f"Missing required columns in CSV: {missing}")
        return
    
    # Optional: Fill NaNs with empty string or None for text columns
    df = df.where(pd.notnull(df), None)

    async with AsyncSessionLocal() as session:
        # Check if table has data to avoid duplicating
        result = await session.execute(text("SELECT COUNT(*) FROM tickets"))
        count = result.scalar()
        if count and count > 0:
            logger.info(f"Database already contains {count} tickets. Skipping seed to prevent duplicates.")
            logger.info("If you want to re-seed, drop the table or run docker-compose down -v.")
            return

        logger.info(f"Preparing {len(df)} records for insertion...")
        
        # We will spread the received_at times over the past 30 days
        now = datetime.now(timezone.utc)
        total_records = len(df)
        
        tickets_to_insert = []
        for idx, row in df.iterrows():
            # Distribute backwards in time
            days_ago = 30 * (total_records - idx) / total_records
            simulated_time = now - timedelta(days=days_ago)
            
            ticket = Ticket(
                ticket_id=uuid4(),
                subject=str(row["subject"]) if row["subject"] else "No Subject",
                body=str(row["body"]) if row["body"] else "No Body",
                timestamp=simulated_time,  # Client timestamp
                language=str(row["language"]) if row["language"] else None,
                queue=str(row["queue"]) if row["queue"] else None,
                type=str(row["type"]) if row["type"] else None,
                received_at=simulated_time, # Server timestamp (historical)
                predicted_priority=str(row["priority"]) if row["priority"] else None
            )
            tickets_to_insert.append(ticket)
            
        session.add_all(tickets_to_insert)
        
        try:
            await session.commit()
            logger.info(f"Successfully inserted {len(tickets_to_insert)} historical tickets into the database.")
        except Exception as exc:
            await session.rollback()
            logger.error(f"Failed to insert records: {exc}")

async def main():
    logger.info("Starting seed script...")
    await seed_data()
    logger.info("Seed script finished.")

if __name__ == "__main__":
    asyncio.run(main())
