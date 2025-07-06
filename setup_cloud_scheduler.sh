#!/bin/bash

# Setup Cloud Scheduler for Multi-Source Data Collection
# This script creates scheduled jobs for Reddit, News, and CoinGecko crawlers

set -e

echo "⏰ Setting up Cloud Scheduler for Multi-Source Data Collection"
echo "=============================================================="

# Configuration
PROJECT_ID="lucky-union-463615-t3"
REGION="us-central1"

# Services and their schedules
SERVICES=(
    "reddit-crawler:0 */2 * * *:Trigger Reddit crawl every 2 hours"
    "news-crawler:30 */2 * * *:Trigger News crawl every 2 hours (offset by 30 min)"
    "coingecko-crawler:15 */1 * * *:Trigger CoinGecko crawl every hour"
)

echo "📋 Setting up ${#SERVICES[@]} scheduled jobs..."

for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service_name schedule description <<< "$service_info"

    echo ""
    echo "🔧 Setting up scheduler for $service_name..."
    echo "   Schedule: $schedule"
    echo "   Description: $description"

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe "$service_name" --region="$REGION" --format="value(status.url)" 2>/dev/null)

    if [ -z "$SERVICE_URL" ]; then
        echo "❌ Service $service_name not found. Please deploy it first."
        continue
    fi

    # Create scheduler job
    JOB_NAME="${service_name}-scheduler"

    # Delete existing job if it exists
    gcloud scheduler jobs delete "$JOB_NAME" --location="$REGION" --quiet 2>/dev/null || true

    # Create new scheduler job
    gcloud scheduler jobs create http "$JOB_NAME" \
        --schedule="$schedule" \
        --uri="$SERVICE_URL" \
        --http-method=POST \
        --location="$REGION" \
        --project="$PROJECT_ID" \
        --description="$description" \
        --headers="Content-Type=application/json"

    echo "✅ Scheduler job created: $JOB_NAME"
done

echo ""
echo "🎉 All Cloud Scheduler jobs created successfully!"
echo ""
echo "📊 Scheduled Jobs:"
for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service_name schedule description <<< "$service_info"
    echo "   - ${service_name}-scheduler: $schedule"
done

echo ""
echo "📝 Management Commands:"
echo "  List jobs: gcloud scheduler jobs list --location=$REGION"
echo "  View job: gcloud scheduler jobs describe JOB_NAME --location=$REGION"
echo "  Pause job: gcloud scheduler jobs pause JOB_NAME --location=$REGION"
echo "  Resume job: gcloud scheduler jobs resume JOB_NAME --location=$REGION"
echo "  Delete job: gcloud scheduler jobs delete JOB_NAME --location=$REGION"

echo ""
echo "🔍 Monitoring:"
echo "  - Scheduler logs: gcloud logging read 'resource.type=cloud_scheduler_job' --limit=20"
echo "  - Service logs: gcloud logging read 'resource.type=cloud_run_revision' --limit=20"
echo "  - GCS data: gsutil ls gs://degen-digest-data/data/ | grep -E '(reddit|news|coingecko)'"

echo ""
echo "✅ Cloud Scheduler setup complete!"

echo "⏰ Setting up Cloud Scheduler for Migration"
echo "==========================================="

# Get the function URL
FUNCTION_URL=$(gcloud functions describe migrate-to-sql --region=us-central1 --format="value(serviceConfig.uri)")

if [ -z "$FUNCTION_URL" ]; then
    echo "❌ Could not get function URL. Make sure the function is deployed."
    exit 1
fi

echo "📡 Function URL: $FUNCTION_URL"

# Create Cloud Scheduler job
gcloud scheduler jobs create http migrate-to-sql-job \
    --schedule="*/30 * * * *" \
    --uri="$FUNCTION_URL" \
    --http-method=POST \
    --location=us-central1 \
    --description="Trigger migration from GCS to Cloud SQL every 30 minutes" \
    --headers="Content-Type=application/json"

echo "✅ Cloud Scheduler job created successfully!"
echo "🔄 Migration will run every 30 minutes"
echo "📊 Monitor at: https://console.cloud.google.com/cloudscheduler"
