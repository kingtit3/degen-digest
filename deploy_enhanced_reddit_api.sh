#!/bin/bash

echo "🚀 Deploying Enhanced Reddit API Crawler to Google Cloud"
echo "=================================================="

# Configuration
SERVICE_NAME="enhanced-reddit-api-crawler"
REGION="us-central1"
PROJECT_ID="lucky-union-463615-t3"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "📦 Building Docker image..."
docker build -t $IMAGE_NAME -f Dockerfile.reddit_api .

echo "📤 Pushing to Google Container Registry..."
docker push $IMAGE_NAME

echo "☁️ Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 900 \
  --concurrency 1 \
  --max-instances 1 \
  --set-env-vars "BUCKET_NAME=degen-digest-data,PROJECT_ID=$PROJECT_ID" \
  --set-env-vars "REDDIT_CLIENT_ID=doW2qicqXIeszi2nTfUfQg,REDDIT_CLIENT_SECRET=cGyFrR80N6bhJb1RYdhj3lIbT9Py9A"

echo "✅ Enhanced Reddit API Crawler deployed successfully!"
echo "🌐 Service URL: https://$SERVICE_NAME-$REGION-$PROJECT_ID.a.run.app"
