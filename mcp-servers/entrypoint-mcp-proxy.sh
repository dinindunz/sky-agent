#!/bin/bash

# Set GitHub token from JSON file if it exists
if [ -f "./keys/github.json" ]; then
    export GITHUB_PERSONAL_ACCESS_TOKEN=$(cat ./keys/github.json | jq -r '.personalAccessToken')
    echo "GitHub token loaded from github.json"
else
    echo "Warning: github.json not found, using environment variable if set"
fi

exec "/root/.local/bin/mcp-proxy" \
    --pass-environment \
    --port=8090 \
    --host=0.0.0.0 \
    --sse-host=0.0.0.0 \
    --named-server-config=./mcp-servers.json