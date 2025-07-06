#!/bin/bash

# Enhanced News Crawler Deployment Script
set -e

echo "🚀 Deploying Enhanced News Crawler..."

# Set environment variables
export PROJECT_ID="lucky-union-463615-t3"
export BUCKET_NAME="degen-digest-data"
export NEWSAPI_KEY="ffc45af6fcd94c4991eaefdc469346e8"

# Create temporary deployment directory
DEPLOY_DIR="temp_news_deploy"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Copy the enhanced news function
cp cloud_function_news.py $DEPLOY_DIR/main.py

# Create requirements.txt for the function
cat > $DEPLOY_DIR/requirements.txt << EOF
functions-framework==3.*
requests==2.31.0
google-cloud-storage==2.10.0
beautifulsoup4==4.12.2
feedparser==6.0.10
vaderSentiment==3.3.2
EOF

# Deploy the function
echo "📦 Deploying enhanced-news-crawler..."
gcloud functions deploy enhanced-news-crawler \
    --runtime python311 \
    --trigger-http \
    --allow-unauthenticated \
    --region us-central1 \
    --source $DEPLOY_DIR \
    --entry-point enhanced_news_crawler \
    --timeout 540s \
    --memory 512MB \
    --set-env-vars PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME,NEWSAPI_KEY=$NEWSAPI_KEY

# Clean up
rm -rf $DEPLOY_DIR

echo "✅ Enhanced News Crawler deployed successfully!"
echo "🔗 Function URL:"
gcloud functions describe enhanced-news-crawler --region=us-central1 --format="value(httpsTrigger.url)"
