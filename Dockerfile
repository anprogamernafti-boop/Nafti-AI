FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Use minimal requirements for speed and reliability
COPY requirements-min.txt ./
RUN pip install --no-cache-dir -r requirements-min.txt

COPY app_simple.py ./

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

# Start gunicorn directly with minimal config
# HF Spaces will restart container if health checks fail
# Response must be fast (< 1 second)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--worker-class", "sync", "--timeout", "60", "--keep-alive", "5", "--access-logfile", "-", "--error-logfile", "-", "app_simple:app"]
