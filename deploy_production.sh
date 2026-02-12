#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

usage() {
  cat <<'EOF'
Usage: ./deploy_production.sh [build|up|down|logs]

Commands:
  build  Build the production image stack from docker-compose.yml
  up     Start production stack in detached mode
  down   Stop production stack and remove orphan containers
  logs   Tail production stack logs
EOF
}

command_build() {
  docker compose -f docker-compose.yml build
}

command_up() {
  docker compose -f docker-compose.yml up -d --build
}

command_down() {
  docker compose -f docker-compose.yml down --remove-orphans
}

command_logs() {
  docker compose -f docker-compose.yml logs -f --tail=200
}

case "${1:-build}" in
  build) command_build ;;
  up) command_up ;;
  down) command_down ;;
  logs) command_logs ;;
  *)
    usage
    exit 1
    ;;
esac
