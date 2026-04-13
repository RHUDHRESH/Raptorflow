#!/bin/bash
# scripts/dev-offline.sh
# Starts the full offline development environment.
# Usage: ./scripts/dev-offline.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "==> Copying offline env files..."
cp "$ROOT_DIR/apps/web/.env.offline" "$ROOT_DIR/apps/web/.env.local"
cp "$ROOT_DIR/crates/.env.offline" "$ROOT_DIR/.env"

echo "==> Starting offline infrastructure (Postgres, Dragonfly, Qdrant, LocalStack, GROQ)..."
docker compose -f "$ROOT_DIR/docker-compose.offline.yml" up -d

echo "==> Waiting for services to be healthy..."
sleep 8

echo "==> Starting mock office WebSocket server..."
node --experimental-vm-modules "$ROOT_DIR/scripts/mock-office-server.ts" &
MOCK_WS_PID=$!

echo ""
echo "==> Offline dev environment ready!"
echo ""
echo "Services:"
echo "  Frontend:  http://localhost:3000 (NEXT_PUBLIC_OFFLINE_MODE=true)"
echo "  API:       http://localhost:8080"
echo "  Postgres:  localhost:5432"
echo "  Dragonfly: localhost:6379"
echo "  Qdrant:    localhost:6333"
echo "  LocalStack: localhost:4566 (SQS + S3)"
echo "  GROQ:      localhost:8081"
echo "  Mock WS:   ws://localhost:3001"
echo ""
echo "Press Ctrl+C to stop all services."

cleanup() {
  echo ""
  echo "==> Stopping services..."
  kill $MOCK_WS_PID 2>/dev/null || true
  docker compose -f "$ROOT_DIR/docker-compose.offline.yml" down
}
trap cleanup EXIT

cd "$ROOT_DIR" && pnpm dev
