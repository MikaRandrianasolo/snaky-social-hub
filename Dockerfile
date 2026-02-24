# Lightweight backend-only Docker image for Railway
# Build stage for frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies and build
RUN npm ci --legacy-peer-deps
COPY frontend/ .
RUN npm run build

# Final stage - Backend only
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
COPY backend/start.sh ./start.sh

# Install Python dependencies using uv
RUN uv sync

# Copy built frontend assets from builder
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Create log directories
RUN mkdir -p /var/log/app

# Ensure start script is executable
RUN chmod +x /app/start.sh || true

# Set up environment variables
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Expose the main port
EXPOSE 8000

# Health check - use the health endpoint with longer startup period
# Use PORT env var (set by platform like Railway) with fallback to 8000
ENV PORT=8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=5 \
    CMD sh -c "curl -f http://localhost:${PORT:-8000}/health || exit 1"

# Start using start script (prints info) which uses PORT/HOST
CMD ["sh", "-c", "./start.sh"]
