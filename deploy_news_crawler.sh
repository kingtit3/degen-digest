#!/bin/bash

echo "🚀 Deploying News Crawler Service..."

# Copy the News Dockerfile to be the main Dockerfile
cp Dockerfile.news Dockerfile

# Build and deploy News crawler
gcloud run deploy news-crawler \
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

echo "✅ News Crawler Service deployed!"
echo "🌐 Service URL: https://news-crawler-128671663649.us-central1.run.app"
echo "⚠️  Don't forget to set NEWSAPI_KEY environment variable!"
