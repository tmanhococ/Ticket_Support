FROM python:3.11-slim

WORKDIR /app

# Install dependencies (build context is project root)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project (preserves src.* package structure)
COPY . .

# Default: run in scheduled mode (infinite loop with schedule library)
# Override with --once for one-shot testing:
#   docker run tickets_drift_monitor --once
CMD ["python", "-m", "src.drift_monitor.run_drift"]
