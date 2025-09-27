#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | sed 's/#.*//' | xargs)
fi

# Build and run sky-agent
docker build --platform linux/amd64 -t sky-agent .

docker run -p 8081:8080 --env-file .env -v ~/.aws:/root/.aws:ro sky-agent