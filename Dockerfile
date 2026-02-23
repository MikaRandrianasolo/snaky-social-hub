# Lightweight backend-only Docker image for Railway
FROM python:3.12-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python dependency management
RUN pip install uv

# Setup directory structure
WORKDIR /app

# Copy backend files
COPY backend/pyproject.toml ./
COPY backend/uv.lock* ./
COPY backend/app ./app
COPY backend/main.py ./
COPY backend/README.md ./

# Install Python dependencies using uv
RUN uv sync

# Create log directories
RUN mkdir -p /var/log/app

# Set up environment variables
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Expose the main port
EXPOSE 8000

# Health check - use the health endpoint with longer startup period
HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Print startup message and start the FastAPI app
CMD sh -c 'echo "Starting Snaky Social Hub API..." && uv run uvicorn main:app --host 0.0.0.0 --port 8000'
