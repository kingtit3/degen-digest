#!/bin/bash

echo "🚀 Deploying Data Aggregator Service..."

# Copy the Data Aggregator Dockerfile to be the main Dockerfile
cp Dockerfile.aggregator Dockerfile

# Build and deploy data aggregator
gcloud run deploy data-aggregator \
  --source . \
  --project=lucky-union-463615-t3 \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --timeout=600 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=lucky-union-463615-t3"

# Restore the original Dockerfile
cp Dockerfile.crawler Dockerfile

echo "✅ Data Aggregator Service deployed!"
echo "🌐 Service URL: https://data-aggregator-128671663649.us-central1.run.app"
