#!/bin/bash
set -euo pipefail

echo "Starting backend on :8000"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting frontend on :3000"
npm run start -- --hostname 0.0.0.0 --port "${PORT:-3000}" &
FRONTEND_PID=$!

cleanup() {
  kill "${BACKEND_PID}" "${FRONTEND_PID}" >/dev/null 2>&1 || true
}

trap cleanup INT TERM EXIT

# Exit when either process exits.
wait -n "${BACKEND_PID}" "${FRONTEND_PID}"
