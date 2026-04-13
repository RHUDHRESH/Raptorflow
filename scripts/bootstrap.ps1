$ErrorActionPreference = "Stop"

corepack enable
pnpm install
pnpm setup:hooks
node scripts/check-foundation-screens.mjs
node scripts/check-job-registry.mjs
node scripts/smoke.mjs
docker compose pull

Write-Host "RaptorFlow scaffold bootstrap complete."
