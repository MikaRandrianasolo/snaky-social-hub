#!/bin/sh
set -e
echo "Starting Snaky Social Hub - start script"
echo "HOST=${HOST:-0.0.0.0}"
echo "PORT=${PORT:-8000}"
echo "PYTHONUNBUFFERED=${PYTHONUNBUFFERED:-1}"

# Optional: wait for a few seconds to allow services to become available
sleep 1

exec uv run uvicorn main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}
