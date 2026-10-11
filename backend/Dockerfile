# ==============================================================================
# Production Dockerfile for Finance Advisor Backend
# Optimized for Render / Cloud Container Deployments
# ==============================================================================
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

# Install system utilities for container healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for caching efficiency
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source
COPY app/ ./app/
COPY .env.example .env.example

# Expose default port
EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start Uvicorn server listening on dynamic platform PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
