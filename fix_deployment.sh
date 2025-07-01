#!/bin/bash

# Fix deployment script for architecture issues

set -e

echo "🔧 Fixing Degen Digest Deployment..."
echo "=" * 50

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No project set. Please set a project:"
    echo "gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Using project: $PROJECT_ID"

# Clean up any existing failed images
echo "🧹 Cleaning up existing images..."
docker rmi gcr.io/$PROJECT_ID/degen_digest_dashboard:latest 2>/dev/null || true

# Build for the correct platform (linux/amd64 for Cloud Run)
echo "🔨 Building new image for linux/amd64..."
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

echo "✅ Fixed deployment complete!"
echo "🌐 Service URL: $SERVICE_URL"

# Force a fresh run
echo "🔄 Forcing fresh run..."
gcloud run services update degen-digest-dashboard \
  --region us-central1 \
  --set-env-vars FORCE_RUN=true,LAST_UPDATE=$(date +%s)

echo "🎉 Fixed deployment and fresh run triggered successfully!"
echo "📊 Check your dashboard at: $SERVICE_URL" 