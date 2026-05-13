#!/usr/bin/env bash
# Store Fivetran credentials in Secret Manager
# Usage: bash scripts/store_secrets.sh

set -euo pipefail

export CLOUDSDK_PYTHON="C:/Python313/python.exe"

echo "========================================"
echo "Fivetran Secret Manager Setup"
echo "========================================"
echo ""
echo "Please enter your Fivetran credentials:"
echo ""

read -p "Fivetran API Key: " API_KEY
read -p "Fivetran API Secret: " API_SECRET

if [ -z "$API_KEY" ] || [ -z "$API_SECRET" ]; then
    echo "Error: Both API Key and Secret are required!"
    exit 1
fi

echo ""
echo "Storing credentials in Secret Manager..."

# Store API Key
echo -n "$API_KEY" | gcloud secrets create fivetran-api-key \
    --data-file=- \
    --replication-policy=automatic \
    --project=bgus-genai-poc2

echo "✓ Stored fivetran-api-key"

# Store API Secret
echo -n "$API_SECRET" | gcloud secrets create fivetran-api-secret \
    --data-file=- \
    --replication-policy=automatic \
    --project=bgus-genai-poc2

echo "✓ Stored fivetran-api-secret"

echo ""
echo "========================================"
echo "✓ Secrets stored successfully!"
echo "========================================"
