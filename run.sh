#!/bin/bash
# Startup script for HF Spaces with optimized Gunicorn settings

echo "[STARTUP] Starting Nafti AI server..."
echo "[STARTUP] Python version: $(python --version)"

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Run gunicorn with optimized settings for HF Spaces healthchecks
python -m gunicorn \
    --workers 1 \
    --worker-class sync \
    --bind 0.0.0.0:5000 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    wsgi:app
