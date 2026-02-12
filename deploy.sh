#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

usage() {
  cat <<'EOF'
Usage: ./deploy.sh [up|down|test]

Commands:
  up     Start local stack (backend + frontend + redis) using docker-compose.local.yml
  down   Stop local stack and remove orphan containers
  test   Run local quality gates (backend unit tests + frontend type/build)
EOF
}

command_up() {
  docker compose -f docker-compose.local.yml up --build
}

command_down() {
  docker compose -f docker-compose.local.yml down --remove-orphans
}

command_test() {
  python -m pytest backend/tests -q --no-cov
  npm run type-check
  npm run build
}

case "${1:-up}" in
  up) command_up ;;
  down) command_down ;;
  test) command_test ;;
  *)
    usage
    exit 1
    ;;
esac
