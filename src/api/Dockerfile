FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
# Note: build context must be project root so requirements.txt is accessible
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project so src/api/ is importable as src.api.* package
COPY . .

EXPOSE 8000

# Health check using Python stdlib — no curl needed in slim image
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
