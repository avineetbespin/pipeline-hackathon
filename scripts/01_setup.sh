#!/usr/bin/env bash
# PipelinePilot — Day 1 GCP setup
# Run from a shell that already has gcloud installed and authenticated.
# Authenticate first if needed:  gcloud auth login && gcloud auth application-default login

set -euo pipefail

# ---- Edit these if needed ----
PROJECT_ID="bgus-genai-poc2"
REGION="us-central1"            # Used for Cloud Run, BigQuery, etc.
                                 # Gemini 3.1 Pro itself runs on the "global" endpoint regardless.
SA_NAME="pipelinepilot-agent"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
# -------------------------------

echo "==> Setting active project to ${PROJECT_ID}"
gcloud config set project "${PROJECT_ID}"
gcloud config set compute/region "${REGION}"

echo "==> Enabling required APIs (this can take 1–2 min)"
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  bigquery.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  cloudfunctions.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  --project="${PROJECT_ID}"

echo "==> Creating service account ${SA_NAME} (idempotent)"
gcloud iam service-accounts create "${SA_NAME}" \
  --display-name="PipelinePilot Agent" \
  --project="${PROJECT_ID}" || echo "   (already exists, continuing)"

echo "==> Granting roles to the service account"
for ROLE in \
  roles/aiplatform.user \
  roles/run.invoker \
  roles/run.developer \
  roles/bigquery.user \
  roles/bigquery.dataEditor \
  roles/bigquery.jobUser \
  roles/secretmanager.secretAccessor \
  roles/cloudscheduler.admin \
  roles/iam.serviceAccountTokenCreator
do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${ROLE}" \
    --condition=None \
    --quiet >/dev/null
  echo "   granted: ${ROLE}"
done

echo "==> Creating BigQuery dataset for PipelinePilot outputs"
bq --location="${REGION}" mk --dataset \
  --description="PipelinePilot agent-managed views and tables" \
  "${PROJECT_ID}:pipelinepilot" 2>/dev/null || echo "   (dataset already exists)"

echo ""
echo "==> Next: store Fivetran credentials in Secret Manager."
echo "   Replace the placeholder values, then run:"
echo ""
echo '   printf "%s" "YOUR_FIVETRAN_API_KEY" | gcloud secrets create fivetran-api-key --data-file=- --replication-policy=automatic'
echo '   printf "%s" "YOUR_FIVETRAN_API_SECRET" | gcloud secrets create fivetran-api-secret --data-file=- --replication-policy=automatic'
echo ""
echo "==> Setup script complete."
