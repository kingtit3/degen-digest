#!/bin/bash

# FarmChecker.xyz Deployment Script
# Deploys the website to Google Cloud Run

set -e

# Configuration
PROJECT_ID="lucky-union-463615-t3"
SERVICE_NAME="farmchecker-website"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Deploying FarmChecker.xyz to Google Cloud Run..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install it first."
    exit 1
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Build the Docker image
echo "🔨 Building Docker image..."
docker build --platform linux/amd64 -t $IMAGE_NAME .

# Push the image to Google Container Registry
echo "📤 Pushing image to Google Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 5000 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "DB_HOST=34.9.71.174,DB_NAME=degen_digest,DB_USER=postgres,DB_PASSWORD=DegenDigest2024!,DB_PORT=5432" \
    --timeout 300

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo "✅ Deployment complete!"
echo "🌐 Your website is available at: $SERVICE_URL"
echo ""
echo "📝 Next steps:"
echo "1. Update your domain DNS to point to: $SERVICE_URL"
echo "2. Set up SSL certificate for your domain"
echo "3. Configure environment variables for database connection"
echo ""
echo "🔧 To update the deployment, run this script again."
