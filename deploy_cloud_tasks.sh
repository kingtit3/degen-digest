#!/bin/bash

# Configuration
PROJECT_ID="lucky-union-463615-t3"
REGION="us-central1"
DEXSCREENER_SERVICE="dexscreener-crawler"
DEXPAPRIKA_SERVICE="dexpaprika-crawler"

echo "🚀 Deploying Crypto Crawlers as Cloud Run Services..."

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudtasks.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudscheduler.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID

# Build and deploy DexScreener service
echo "📦 Building and deploying DexScreener service..."
gcloud run deploy $DEXSCREENER_SERVICE \
    --source . \
    --platform managed \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --set-env-vars "PYTHONPATH=/app"

# Build and deploy DexPaprika service
echo "📦 Building and deploying DexPaprika service..."
gcloud run deploy $DEXPAPRIKA_SERVICE \
    --source . \
    --platform managed \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --set-env-vars "PYTHONPATH=/app"

# Get service URLs
DEXSCREENER_URL=$(gcloud run services describe $DEXSCREENER_SERVICE --region=$REGION --format="value(status.url)" 2>/dev/null)
DEXPAPRIKA_URL=$(gcloud run services describe $DEXPAPRIKA_SERVICE --region=$REGION --format="value(status.url)" 2>/dev/null)

echo "✅ Services deployed successfully!"
echo "DexScreener URL: $DEXSCREENER_URL"
echo "DexPaprika URL: $DEXPAPRIKA_URL"

# Create Cloud Tasks queues
echo "📋 Creating Cloud Tasks queues..."
gcloud tasks queues create dexscreener-queue \
    --location=$REGION \
    --project=$PROJECT_ID \
    --max-concurrent-dispatches=1 \
    --max-attempts=3

gcloud tasks queues create dexpaprika-queue \
    --location=$REGION \
    --project=$PROJECT_ID \
    --max-concurrent-dispatches=1 \
    --max-attempts=3

echo "✅ Cloud Tasks queues created!"

# Create Cloud Scheduler jobs (every 2 hours)
echo "⏰ Creating Cloud Scheduler jobs..."

# DexScreener scheduler (every 2 hours)
gcloud scheduler jobs create http dexscreener-scheduler \
    --schedule="0 */2 * * *" \
    --uri="$DEXSCREENER_URL" \
    --http-method=POST \
    --location=$REGION \
    --project=$PROJECT_ID \
    --description="Trigger DexScreener crawl every 2 hours"

# DexPaprika scheduler (every 2 hours, offset by 1 hour)
gcloud scheduler jobs create http dexpaprika-scheduler \
    --schedule="0 1-23/2 * * *" \
    --uri="$DEXPAPRIKA_URL" \
    --http-method=POST \
    --location=$REGION \
    --project=$PROJECT_ID \
    --description="Trigger DexPaprika crawl every 2 hours (offset)"

echo "✅ Cloud Scheduler jobs created!"

echo ""
echo "🎯 Deployment Summary:"
echo "======================"
echo "DexScreener Service: $DEXSCREENER_URL"
echo "DexPaprika Service:  $DEXPAPRIKA_URL"
echo "DexScreener Schedule: Every 2 hours (0:00, 2:00, 4:00, etc.)"
echo "DexPaprika Schedule:  Every 2 hours (1:00, 3:00, 5:00, etc.)"
echo ""
echo "📊 Monitoring:"
echo "  - Cloud Run logs: gcloud logging read 'resource.type=cloud_run_revision' --limit=50"
echo "  - Scheduler logs: gcloud scheduler jobs list"
echo "  - GCS files: gsutil ls gs://degen-digest-data/data/ | grep -E '(dexscreener|dexpaprika)'"
echo ""
echo "🔄 Manual triggers:"
echo "  - DexScreener: curl -X POST $DEXSCREENER_URL"
echo "  - DexPaprika:  curl -X POST $DEXPAPRIKA_URL"
