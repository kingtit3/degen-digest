#!/bin/bash

echo "🚀 Deploying Fixed Migration Cloud Function"
echo "=========================================="

# Set environment variables
export DB_HOST="34.9.71.174"
export DB_PORT="5432"
export DB_NAME="degen_digest"
export DB_USER="postgres"
export DB_PASSWORD="DegenDigest2024!"
export BUCKET_NAME="degen-digest-data"
export PROJECT_ID="lucky-union-463615-t3"

# Create a clean deployment directory
rm -rf migration_deploy
mkdir -p migration_deploy

# Copy only the necessary files
cp cloud_function/migrate_to_sql.py migration_deploy/main.py
cp cloud_function/requirements.txt migration_deploy/requirements.txt

# Deploy the function
gcloud functions deploy migrate-to-sql-fixed \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=migration_deploy \
  --entry-point=migrate \
  --trigger-http \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=540s \
  --set-env-vars="DB_HOST=${DB_HOST},DB_PORT=${DB_PORT},DB_NAME=${DB_NAME},DB_USER=${DB_USER},DB_PASSWORD=${DB_PASSWORD},BUCKET_NAME=${BUCKET_NAME},PROJECT_ID=${PROJECT_ID}"

echo "✅ Fixed migration function deployed successfully!"
echo ""
echo "🔧 To run the migration:"
echo "gcloud functions call migrate-to-sql-fixed --region=us-central1"
