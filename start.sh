#!/bin/bash
set -e

echo "Starting Statishub API..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Wait for Redis to be ready
echo "Waiting for Redis..."
timeout=30
while ! redis-cli -h ${REDIS_HOST:-localhost} -p ${REDIS_PORT:-6379} ping > /dev/null 2>&1; do
    timeout=$((timeout - 1))
    if [ $timeout -le 0 ]; then
        echo "Error: Redis not available after 30 seconds"
        exit 1
    fi
    sleep 1
done
echo "Redis is ready!"

# Start the application
echo "Starting Uvicorn..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --log-level ${LOG_LEVEL:-info}
