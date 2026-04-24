#!/usr/bin/env sh
set -eu

export PNPM_HOME="${PNPM_HOME:-/pnpm/home}"
export PNPM_STORE_DIR="${PNPM_STORE_DIR:-/pnpm/store}"

corepack enable

manifest_hash="$(sha256sum \
  /workspace/package.json \
  /workspace/pnpm-workspace.yaml \
  /workspace/turbo.json \
  /workspace/apps/web/package.json \
  | sha256sum \
  | awk '{print $1}')"

stamp_file="/workspace/node_modules/.raptorflow-manifest.hash"
app_next_bin="/workspace/apps/web/node_modules/next/dist/bin/next"
previous_hash=""

if [ -f "$stamp_file" ]; then
  previous_hash="$(cat "$stamp_file")"
fi

if [ ! -d /workspace/node_modules ] || [ ! -f "$app_next_bin" ] || [ "$previous_hash" != "$manifest_hash" ]; then
  pnpm install --store-dir "$PNPM_STORE_DIR" --prefer-offline --no-frozen-lockfile
  mkdir -p /workspace/node_modules
  printf '%s\n' "$manifest_hash" > "$stamp_file"
fi

cd /workspace/apps/web

rm -rf .next

exec pnpm --filter @raptorflow/web dev --hostname 0.0.0.0 --port 3000
