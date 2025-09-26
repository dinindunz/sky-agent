FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install Claude Code SDK
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @anthropic-ai/claude-code && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Google Cloud SDK
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update && apt-get install -y google-cloud-cli \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN uv sync

COPY . .

# Add build args for GCP environment variables
ARG CLOUDSDK_CORE_PROJECT
ARG CLOUDSDK_COMPUTE_REGION
ARG CLOUDSDK_COMPUTE_ZONE
ARG GOOGLE_APPLICATION_CREDENTIALS

# Configure gcloud with service account
RUN if [ -f "/app/keys/gcp.json" ]; then \
        gcloud auth activate-service-account \
            --key-file=/app/keys/gcp.json \
            --project=${CLOUDSDK_CORE_PROJECT} \
        && gcloud config set project ${CLOUDSDK_CORE_PROJECT} \
        && gcloud config set compute/region ${CLOUDSDK_COMPUTE_REGION} \
        && gcloud config set compute/zone ${CLOUDSDK_COMPUTE_ZONE} \
        && gcloud config set core/disable_prompts true \
        && gcloud config set core/disable_usage_reporting true \
        && gcloud config set component_manager/disable_update_check true; \
    else \
        echo "Warning: GCP service account key not found at /app/keys/gcp.json"; \
    fi

EXPOSE 8081

CMD ["uv", "run", "sky-agent"]
