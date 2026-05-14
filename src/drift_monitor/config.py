"""
src/drift_monitor/config.py
----------------------------
Configuration for the Drift Monitor service.

All values are read from environment variables with safe defaults.
"""

import os


# PostgreSQL — synchronous psycopg2 URL (dashboard pattern, not asyncpg)
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://tickets_user:tickets_pass@db:5432/tickets_db",
).replace("postgresql+asyncpg://", "postgresql://")

# AWS / S3
S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "")
AWS_REGION: str = os.getenv("AWS_REGION", "ap-southeast-1")

# Drift monitor output
REPORT_OUTPUT_DIR: str = os.getenv("REPORT_OUTPUT_DIR", "/tmp/drift_reports")

# Window sizes
# How many recent tickets to treat as "current" production data
CURRENT_WINDOW_HOURS: int = int(os.getenv("CURRENT_WINDOW_HOURS", "24"))
# How many tickets to use as reference baseline
REFERENCE_SAMPLE_SIZE: int = int(os.getenv("REFERENCE_SAMPLE_SIZE", "500"))

# Schedule interval in hours (for continuous mode)
SCHEDULE_INTERVAL_HOURS: int = int(os.getenv("SCHEDULE_INTERVAL_HOURS", "6"))
