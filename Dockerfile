# Build stage for frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy frontend source
COPY frontend/ .

# Build frontend
RUN npm run build

# Final stage - Combined backend and frontend
FROM python:3.12-slim

# Install system dependencies (nginx, supervisor for process management, git)
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    git \
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

# Copy built frontend assets from builder
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Copy nginx configuration
COPY frontend/nginx.conf /etc/nginx/nginx.conf

# Create log directories
RUN mkdir -p /var/log/supervisor /var/run/nginx

# Set up environment variables
ENV PORT=8000
ENV HOST=0.0.0.0

# Expose the main port
EXPOSE 8000

# Health check - use the health endpoint with longer startup period
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the FastAPI app directly (Railway will handle process management)
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
