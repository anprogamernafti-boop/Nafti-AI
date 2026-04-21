FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Use minimal requirements for speed and reliability
COPY requirements-min.txt ./
RUN pip install --no-cache-dir -r requirements-min.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

# Use Python monitor to avoid HF Spaces 30-min timeout
# The script monitors and restarts the app every 25 minutes
CMD ["python", "/app/monitor.py"]
