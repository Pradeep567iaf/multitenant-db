#!/bin/bash
# Render start script for FastAPI + Celery

echo "🚀 Starting Multi-Tenant System..."

# Start Celery worker in background
echo "🔧 Starting Celery worker..."
celery -A celery_worker_render_compatible worker --loglevel=info --concurrency=1 &
CELERY_PID=$!

# Wait a moment for Celery to start
sleep 5

# Start FastAPI application
echo "⚡ Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Cleanup on exit
trap "kill $CELERY_PID" EXIT