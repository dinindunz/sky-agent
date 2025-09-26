#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Build and run sky-agent
docker build --platform linux/amd64 \
  --build-arg CLOUDSDK_CORE_PROJECT=${CLOUDSDK_CORE_PROJECT} \
  --build-arg CLOUDSDK_COMPUTE_REGION=${CLOUDSDK_COMPUTE_REGION} \
  --build-arg CLOUDSDK_COMPUTE_ZONE=${CLOUDSDK_COMPUTE_ZONE} \
  --build-arg GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} \
  -t sky-agent .

docker run -p 8081:8080 --env-file .env -v ~/.aws:/root/.aws:ro sky-agent