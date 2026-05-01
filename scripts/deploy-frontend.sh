#!/bin/bash
# scripts/deploy-frontend.sh
# Deploys the Next.js frontend to Vercel.
# Usage: ./scripts/deploy-frontend.sh [--production]
#
# Prerequisites:
#   - VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID env vars set
#   - Run once: vercel link --token=$VERCEL_TOKEN

set -e

PRODUCTION=""
if [ "$1" = "--production" ]; then
  PRODUCTION="--prod"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "==> Building frontend..."
pnpm --filter @raptorflow/web build

echo "==> Deploying to Vercel..."
vercel deploy $PRODUCTION \
  --token="$VERCEL_TOKEN" \
  --cwd="$ROOT_DIR" \
  --yes

echo "==> Done."
