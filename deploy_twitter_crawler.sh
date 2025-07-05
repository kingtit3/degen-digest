#!/bin/bash

echo "🚀 Deploying Twitter Crawler Service..."

# Copy the Twitter Dockerfile to be the main Dockerfile
cp Dockerfile.twitter Dockerfile

# Build and deploy Twitter crawler
gcloud run deploy twitter-crawler \
  --source . \
  --project=lucky-union-463615-t3 \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --timeout=1800 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=lucky-union-463615-t3"

# Restore the original Dockerfile
cp Dockerfile.crawler Dockerfile

echo "✅ Twitter Crawler Service deployed!"
echo "🌐 Service URL: https://twitter-crawler-128671663649.us-central1.run.app"
echo "⚠️  Don't forget to set TWITTER_USERNAME and TWITTER_PASSWORD environment variables!"
