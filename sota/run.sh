#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Build frontend
echo "Building frontend..."
cd frontend && bun install && bun run build && cd ..

# Start server
source ~/repos/j2/.venv/bin/activate
echo "Starting server at http://localhost:8001"
uvicorn main:app --host 0.0.0.0 --port 8001
