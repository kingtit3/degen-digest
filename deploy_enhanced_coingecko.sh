#!/bin/bash

# Enhanced CoinGecko Crawler Deployment Script
set -e

echo "🚀 Deploying Enhanced CoinGecko Crawler..."

# Set environment variables
export PROJECT_ID="lucky-union-463615-t3"
export BUCKET_NAME="degen-digest-data"

# Create temporary deployment directory
DEPLOY_DIR="temp_coingecko_deploy"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Copy the enhanced CoinGecko function
cp cloud_function_coingecko.py $DEPLOY_DIR/main.py

# Create requirements.txt for the function
cat > $DEPLOY_DIR/requirements.txt << EOF
functions-framework==3.*
requests==2.31.0
google-cloud-storage==2.10.0
EOF

# Deploy the function
echo "📦 Deploying enhanced-coingecko-crawler..."
gcloud functions deploy enhanced-coingecko-crawler \
    --runtime python311 \
    --trigger-http \
    --allow-unauthenticated \
    --region us-central1 \
    --source $DEPLOY_DIR \
    --entry-point enhanced_coingecko_crawler \
    --timeout 540s \
    --memory 512MB \
    --set-env-vars PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME

# Clean up
rm -rf $DEPLOY_DIR

echo "✅ Enhanced CoinGecko Crawler deployed successfully!"
echo "🔗 Function URL:"
gcloud functions describe enhanced-coingecko-crawler --region=us-central1 --format="value(httpsTrigger.url)"
