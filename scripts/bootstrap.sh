#!/usr/bin/env sh
set -eu

corepack enable
pnpm install
pnpm setup:hooks
node scripts/check-foundation-screens.mjs
node scripts/check-job-registry.mjs
node scripts/smoke.mjs
docker compose pull

echo "RaptorFlow scaffold bootstrap complete."
