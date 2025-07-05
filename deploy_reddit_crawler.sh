#!/bin/bash

echo "🚀 Deploying Reddit Crawler Service..."

# Copy the Reddit Dockerfile to be the main Dockerfile
cp Dockerfile.reddit Dockerfile

# Build and deploy Reddit crawler
gcloud run deploy reddit-crawler \
  --source . \
  --project=lucky-union-463615-t3 \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=lucky-union-463615-t3"

# Restore the original Dockerfile
cp Dockerfile.crawler Dockerfile

echo "✅ Reddit Crawler Service deployed!"
echo "🌐 Service URL: https://reddit-crawler-128671663649.us-central1.run.app"
