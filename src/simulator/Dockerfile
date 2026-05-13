FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
# Note: build context must be project root so requirements.txt is accessible
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project so src/simulator/ is importable as src.simulator.* package
COPY . .

# Default: run simulator against the API service on internal Docker network
CMD ["python", "-m", "src.simulator.run_simulator", \
     "--url", "http://api:8000", \
     "--rate", "1"]
