#!/bin/bash

# Build and run sky-swarm agent
docker build --platform linux/amd64 -t sky-swarm .
docker run -p 8081:8080 --env-file .env -v ~/.aws:/root/.aws:ro sky-swarm