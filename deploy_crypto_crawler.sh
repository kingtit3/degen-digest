#!/bin/bash

echo "🚀 Deploying Crypto Crawler Service..."

# Copy the Crypto Dockerfile to be the main Dockerfile
cp Dockerfile.crypto Dockerfile

# Build and deploy Crypto crawler
gcloud run deploy crypto-crawler \
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

echo "✅ Crypto Crawler Service deployed!"
echo "🌐 Service URL: https://crypto-crawler-128671663649.us-central1.run.app"
