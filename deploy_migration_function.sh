#!/bin/bash

echo "🚀 Deploying Migration Cloud Function"
echo "====================================="

# Set environment variables with proper escaping
export DB_HOST="34.9.71.174"
export DB_PORT="5432"
export DB_NAME="degen_digest"
export DB_USER="postgres"
export DB_PASSWORD="DegenDigest2024!"
export BUCKET_NAME="degen-digest-data"
export PROJECT_ID="lucky-union-463615-t3"

# Deploy the function
gcloud functions deploy migrate-to-sql \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=cloud_function \
  --entry-point=migrate \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars="DB_HOST=${DB_HOST},DB_PORT=${DB_PORT},DB_NAME=${DB_NAME},DB_USER=${DB_USER},DB_PASSWORD=${DB_PASSWORD},BUCKET_NAME=${BUCKET_NAME},PROJECT_ID=${PROJECT_ID}"

echo "✅ Migration function deployed successfully!"
