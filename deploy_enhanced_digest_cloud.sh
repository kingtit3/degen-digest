#!/bin/bash

# Enhanced Digest Cloud Function Deployment Script
set -e

echo "🚀 Deploying Enhanced Digest Cloud Function..."

# Set environment variables
export PROJECT_ID="lucky-union-463615-t3"
export BUCKET_NAME="degen-digest-data"

# Create temporary deployment directory
DEPLOY_DIR="temp_digest_deploy"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Copy the digest cloud function
cp cloud_function/digest_main.py $DEPLOY_DIR/main.py
cp cloud_function/requirements.txt $DEPLOY_DIR/requirements.txt

# Deploy the function
echo "📦 Deploying enhanced-digest-cloud..."
gcloud functions deploy enhanced-digest-cloud \
    --runtime python311 \
    --trigger-http \
    --allow-unauthenticated \
    --region us-central1 \
    --source $DEPLOY_DIR \
    --entry-point enhanced_digest_cloud \
    --timeout 540s \
    --memory 512MB \
    --set-env-vars PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME

# Clean up
rm -rf $DEPLOY_DIR

echo "✅ Enhanced Digest Cloud Function deployed successfully!"
echo "🔗 Function URL:"
gcloud functions describe enhanced-digest-cloud --region=us-central1 --format="value(httpsTrigger.url)"
