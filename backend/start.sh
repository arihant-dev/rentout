#!/bin/sh
echo "==== container start script ===="
echo "PORT=${PORT:-8080}"
echo "Environment variables:"
env
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Files in /app:"
ls -la /app || true
echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --log-level debug
