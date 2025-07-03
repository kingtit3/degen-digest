#!/bin/bash

# Deploy Continuous Solana Crawler to Google Cloud
set -e

echo "🚀 Deploying Continuous Solana Crawler to Google Cloud..."

# Configuration
PROJECT_ID="lucky-union-463615-t3"
REGION="us-central1"
SERVICE_NAME="solana-crawler"
REPOSITORY="degendigest-crawler"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "📋 Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"
echo "   Repository: $REPOSITORY"
echo ""

# Set project
echo "🔧 Setting Google Cloud project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Create Artifact Registry repository if it doesn't exist
echo "📦 Creating Artifact Registry repository..."
gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --description="DegenDigest Solana Crawler" \
    --quiet || echo "Repository already exists"

# Configure Docker to use gcloud as a credential helper
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker

# Build and push the Docker image
echo "🏗️ Building Docker image..."
docker build --platform=linux/amd64 -f Dockerfile.crawler -t $IMAGE_NAME .

echo "📤 Pushing image to Artifact Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 1 \
    --min-instances 1 \
    --concurrency 1 \
    --set-env-vars="PYTHONPATH=/app" \
    --set-env-vars="PLAYWRIGHT_BROWSERS_PATH=/ms-playwright"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo "✅ Deployment successful!"
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "📊 To monitor the crawler:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION"
echo "   gcloud logs read --service=$SERVICE_NAME --limit=50"
echo ""
echo "🛑 To stop the crawler:"
echo "   gcloud run services delete $SERVICE_NAME --region=$REGION"
