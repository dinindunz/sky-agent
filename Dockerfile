FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    lsb-release \
    jq \
    curl \
    gnupg \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Azure CLI
RUN apt-get update && apt-get install -y \
    && curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" | tee -a /etc/apt/sources.list.d/azure-cli.list \
    && apt-get update && apt-get install -y azure-cli \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Google Cloud CLI
RUN apt-get update && apt-get install -y \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update && apt-get install -y google-cloud-cli \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Claude Code SDK
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @anthropic-ai/claude-code && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN uv sync

COPY . .

# Configure Azure CLI with service principal
RUN if [ -f "/app/keys/azure.json" ]; then \
        az login --service-principal \
            --username $(cat /app/keys/azure.json | jq -r '.appId') \
            --password $(cat /app/keys/azure.json | jq -r '.clientSecret') \
            --tenant $(cat /app/keys/azure.json | jq -r '.tenantId'); \
    else \
        echo "Warning: Azure config not found at /app/keys/azure.json"; \
    fi

# Configure Google Cloud CLI
RUN if [ -f "/app/keys/gcp.json" ]; then \
        gcloud auth activate-service-account \
            --key-file=/app/keys/gcp.json \
            --project=$(cat /app/keys/gcp.json | jq -r '.project_id') \
    else \
        echo "Warning: GCP config not found at /app/keys/gcp.json"; \
    fi

EXPOSE 8081

CMD ["uv", "run", "sky-agent"]
