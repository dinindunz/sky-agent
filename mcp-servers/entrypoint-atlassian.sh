#!/bin/sh

# Set Atlassian environment variables from JSON file if it exists
if [ -f "/app/keys/atlassian.json" ]; then
    export CONFLUENCE_URL=$(cat /app/keys/atlassian.json | jq -r ".instanceUrl")
    export CONFLUENCE_USERNAME=$(cat /app/keys/atlassian.json | jq -r ".email")
    export CONFLUENCE_API_TOKEN=$(cat /app/keys/atlassian.json | jq -r ".apiToken")
    export JIRA_URL=$(cat /app/keys/atlassian.json | jq -r ".instanceUrl")
    export JIRA_USERNAME=$(cat /app/keys/atlassian.json | jq -r ".email")
    export JIRA_API_TOKEN=$(cat /app/keys/atlassian.json | jq -r ".apiToken")
    echo "Environment variables set from atlassian.json"
else
    echo "Warning: Atlassian config not found at /app/keys/atlassian.json"
fi

# Execute the MCP Atlassian server with passed arguments
exec /app/.venv/bin/mcp-atlassian "$@"