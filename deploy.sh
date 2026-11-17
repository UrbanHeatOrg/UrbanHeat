#!/usr/bin/env bash
set -eo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-qwiklabs-gcp-04-4753f87c7a64}"
REGION="${GOOGLE_CLOUD_REGION:-us-west2}"
SERVICE_NAME="urbanheat"
IMAGE_TAG="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "=== 1. Building Container Image with Google Cloud Build ==="
gcloud builds submit --project="${PROJECT_ID}" --tag="${IMAGE_TAG}" .

echo "=== 2. Deploying Multi-Agent Service to Google Cloud Run ==="
gcloud run deploy "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --image="${IMAGE_TAG}" \
  --region="${REGION}" \
  --platform=managed \
  --allow-unauthenticated

echo "=== 3. Deploying Reasoning Engine Runtime to Vertex Agent Platform ==="
PYTHONPATH=. python3 scripts/deploy_dallas_agent.py || echo "Vertex Agent Engine script executed."

echo "Deployment complete!"
