#!/bin/bash

# Degen Digest Dashboard Deployment Script
# This script deploys the dashboard to Google Cloud Run and forces a fresh run

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

# Build the Docker image for linux/amd64 (Cloud Run requirement)
echo "🔨 Building Docker image for linux/amd64..."
docker build --platform linux/amd64 -f Dockerfile.dashboard -t gcr.io/$PROJECT_ID/degen_digest_dashboard:latest .

# Push to Container Registry
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
  --timeout 3600 \
  --concurrency 80 \
  --max-instances 10

# Get the service URL
SERVICE_URL=$(gcloud run services describe degen-digest-dashboard --region=us-central1 --format="value(status.url)")

echo "✅ Deployment complete!"
echo "🌐 Service URL: $SERVICE_URL"

# Force a fresh run by updating environment variables
echo "🔄 Forcing fresh run..."
gcloud run services update degen-digest-dashboard \
  --region us-central1 \
  --set-env-vars FORCE_RUN=true,LAST_UPDATE=$(date +%s)

echo "🎉 Deployment and fresh run triggered successfully!"
echo "📊 Check your dashboard at: $SERVICE_URL"
echo "📝 Check logs with: gcloud logging tail \"resource.type=cloud_run_revision AND resource.labels.service_name=degen-digest-dashboard\"" 