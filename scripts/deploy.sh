#!/usr/bin/env bash
#
# City of Dallas — Urban Heat Resilience Deployment Script
# Automatically builds and deploys the Agent & Dashboard to Google Cloud Run.
#
# Usage:
#   bash scripts/deploy.sh                        # Deploy to default project & region
#   bash scripts/deploy.sh --service my-service   # Deploy with custom service name
#   bash scripts/deploy.sh --region us-central1   # Deploy to a specific GCP region
#   bash scripts/deploy.sh --api-key AIzaSy...    # Deploy with a Gemini API key
#   bash scripts/deploy.sh --help                 # Show usage options
#

set -euo pipefail

# --------------------------------------------------------------------------
# Formatting Helpers
# --------------------------------------------------------------------------
bold() { printf '\033[1m%s\033[0m\n' "$*"; }
info() { printf '  \033[34mℹ\033[0m %s\n' "$*"; }
success() { printf '  \033[32m✔\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m⚠\033[0m %s\n' "$*"; }
fail() { printf '\n\033[1;31mERROR:\033[0m %s\n\n' "$*" >&2; exit 1; }

# --------------------------------------------------------------------------
# Default Settings
# --------------------------------------------------------------------------
DEFAULT_PROJECT="$(gcloud config get-value project 2>/dev/null || echo 'climate-heat-challenge')"
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$DEFAULT_PROJECT}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-west1}"
SERVICE_NAME="urbanheat"
API_KEY="${GEMINI_API_KEY:-}"
USE_VERTEX="1"

# --------------------------------------------------------------------------
# CLI Argument Parsing
# --------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --project|-p)
      PROJECT_ID="$2"
      shift 2
      ;;
    --region|-r)
      REGION="$2"
      shift 2
      ;;
    --service|-s)
      SERVICE_NAME="$2"
      shift 2
      ;;
    --api-key|-k)
      API_KEY="$2"
      USE_VERTEX="0"
      shift 2
      ;;
    --help|-h)
      bold "Usage: bash scripts/deploy.sh [OPTIONS]"
      echo
      echo "Options:"
      echo "  -p, --project  <PROJECT_ID>   Google Cloud Project ID (default: current gcloud project)"
      echo "  -r, --region   <REGION>       Cloud Run Region (default: us-west1)"
      echo "  -s, --service  <SERVICE_NAME> Service Name in Cloud Run (default: urbanheat)"
      echo "  -k, --api-key  <KEY>          Google AI Studio Gemini API Key (bypasses Vertex AI terms)"
      echo "  -h, --help                    Show this help message and exit"
      echo
      echo "Example:"
      echo "  bash scripts/deploy.sh --service urbanheat-track1 --region us-west1"
      exit 0
      ;;
    *)
      fail "Unknown option: $1. Run 'bash scripts/deploy.sh --help' for usage."
      ;;
  esac
done

# If API_KEY is set in environment, toggle Vertex off
if [[ -n "$API_KEY" ]]; then
  USE_VERTEX="0"
fi

bold "==================================================================="
bold "🚀 Deploying Dallas Urban Heat Resilience Agent & Dashboard"
bold "==================================================================="
info "Project ID   : $PROJECT_ID"
info "Region       : $REGION"
info "Service Name : $SERVICE_NAME"
info "Backend Mode : $([[ "$USE_VERTEX" == "1" ]] && echo 'Vertex AI (Enterprise)' || echo 'Gemini Developer API (API Key)')"
echo

# --------------------------------------------------------------------------
# Pre-flight Checks
# --------------------------------------------------------------------------
bold "[1/4] Checking Google Cloud environment..."
if ! command -v gcloud &>/dev/null; then
  fail "gcloud CLI is not installed or not in PATH. Please run from Google Cloud Shell or install Google Cloud SDK."
fi

# Ensure active project is set
gcloud config set project "$PROJECT_ID" --quiet &>/dev/null || warn "Could not set default project to $PROJECT_ID."

# Enable required Google Cloud services
info "Enabling required Google Cloud APIs (Cloud Run, Cloud Build, Vertex AI, BigQuery)..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  --project="$PROJECT_ID" --quiet || warn "API activation skipped (requires Service Usage Admin, proceeding with deployment)..."

success "Pre-flight checks passed."
echo

# --------------------------------------------------------------------------
# IAM Role Assignment for Cloud Run Service Account
# --------------------------------------------------------------------------
bold "[2/4] Verifying Cloud Run Service Account permissions..."
PROJECT_NUM="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)' 2>/dev/null || true)"
if [[ -n "$PROJECT_NUM" ]]; then
  COMPUTE_SA="${PROJECT_NUM}-compute@developer.gserviceaccount.com"
  info "Granting Vertex AI and BigQuery access to: $COMPUTE_SA"
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/aiplatform.user" --quiet &>/dev/null || true
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="roles/bigquery.user" --quiet &>/dev/null || true
  success "IAM service account roles configured."
else
  warn "Could not resolve project number. Skipping automatic service account binding."
fi
echo

# --------------------------------------------------------------------------
# Prepare Environment Variables
# --------------------------------------------------------------------------
bold "[3/4] Building Cloud Run deployment configuration..."
ENV_VARS="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=global,GOOGLE_GENAI_USE_VERTEXAI=${USE_VERTEX}"

if [[ -n "$API_KEY" ]]; then
  ENV_VARS="${ENV_VARS},GEMINI_API_KEY=${API_KEY}"
fi

# --------------------------------------------------------------------------
# Deploy to Cloud Run
# --------------------------------------------------------------------------
bold "[4/4] Building container and deploying to Cloud Run..."
info "Running: gcloud run deploy $SERVICE_NAME --source . --region $REGION --allow-unauthenticated"
echo

if gcloud run deploy "$SERVICE_NAME" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --source=. \
  --allow-unauthenticated \
  --set-env-vars="$ENV_VARS" \
  --quiet; then

  SERVICE_URL="$(gcloud run services describe "$SERVICE_NAME" --project="$PROJECT_ID" --region="$REGION" --format='value(status.url)' 2>/dev/null || true)"

  echo
  bold "==================================================================="
  printf '\033[1;32m%s\033[0m\n' "🎉 DEPLOYMENT SUCCEEDED!"
  bold "==================================================================="
  echo "  Live Service URL:"
  printf '  \033[1;36m%s\033[0m\n' "$SERVICE_URL"
  echo
  echo "  Open this link in your browser to access:"
  echo "    • Interactive Dallas Urban Heat Leaflet Map"
  echo "    • ⚡ Track 1: 102° Hydration & Wellness Dispatch"
  echo "    • 🌳 Track 3: Tree Planting ROI"
  echo "    • 🏛️ Track 2: Siting Recommendations & Equity Audit"
  echo "    • Dana AI Planning Copilot (Gemini-powered)"
  bold "==================================================================="
  echo
else
  fail "Deployment to Cloud Run failed. Please review the build logs above."
fi
