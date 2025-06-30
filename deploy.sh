#!/bin/bash

# Degen Digest Dashboard Deployment Script
# This script deploys the dashboard to Google Cloud Run

set -e

echo "🚀 Deploying Degen Digest Dashboard to Google Cloud Run..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first:"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud. Please run:"
    echo "gcloud auth login"
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No project set. Please set a project:"
    echo "gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Using project: $PROJECT_ID"

# Build and push the Docker image
echo "🔨 Building Docker image..."
docker build -f Dockerfile.dashboard -t gcr.io/$PROJECT_ID/degen_digest_dashboard:latest .

echo "📤 Pushing to Container Registry..."
docker push gcr.io/$PROJECT_ID/degen_digest_dashboard:latest

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy degen-digest-dashboard \
    --image gcr.io/$PROJECT_ID/degen_digest_dashboard:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8501 \
    --memory 4Gi \
    --cpu 2 \
    --max-instances 10 \
    --timeout 300 \
    --set-env-vars STREAMLIT_SERVER_PORT=8501,STREAMLIT_SERVER_ADDRESS=0.0.0.0,STREAMLIT_SERVER_HEADLESS=true

echo "✅ Deployment complete!"
echo "🌐 Your dashboard is now live at:"
gcloud run services describe degen-digest-dashboard --region=us-central1 --format="value(status.url)"

echo ""
echo "📊 To view logs:"
echo "gcloud logs tail --service=degen-digest-dashboard --region=us-central1" 