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

# Create log directories for supervisor
RUN mkdir -p /var/log/supervisor

# Copy supervisor configuration
RUN mkdir -p /etc/supervisor/conf.d
COPY <<EOF /etc/supervisor/conf.d/supervisord.conf
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log

[program:backend]
command=uv run uvicorn main:app --host 127.0.0.1 --port 8000
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/backend.log
stderr_logfile=/var/log/supervisor/backend_err.log

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/nginx.log
stderr_logfile=/var/log/supervisor/nginx_err.log
EOF

# Expose the main port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/docs || exit 1

# Start supervisor which manages both backend and nginx
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
