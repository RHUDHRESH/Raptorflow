#!/bin/bash
# Wrapper script for gcloud MCP to ensure gcloud is in PATH

# Set up environment
GCLOUD_BIN="/c/Users/hp/AppData/Local/Google/Cloud SDK/google-cloud-sdk/bin"
GCLOUD_SDK_ROOT="/c/Users/hp/AppData/Local/Google/Cloud SDK/google-cloud-sdk"

# Export all necessary variables
export PATH="${GCLOUD_BIN}:${PATH}"
export CLOUDSDK_ROOT_DIR="${GCLOUD_SDK_ROOT}"
export CLOUDSDK_PYTHON="python"

# Verify gcloud executable exists
if [ ! -x "${GCLOUD_BIN}/gcloud" ]; then
    echo "Error: gcloud executable not found at ${GCLOUD_BIN}/gcloud" >&2
    exit 1
fi

# Run the gcloud MCP server
npx -y @google-cloud/gcloud-mcp "$@"
