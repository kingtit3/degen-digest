#!/bin/bash

# Deploy Cloud Tasks for Multi-Source Data Collection
# This script deploys Reddit, News, and CoinGecko crawlers to Google Cloud Run

set -e

echo "🚀 Deploying Cloud Tasks for Multi-Source Data Collection"
echo "=========================================================="

# Configuration
PROJECT_ID="lucky-union-463615-t3"
REGION="us-central1"
BUCKET_NAME="degen-digest-data"

# Services to deploy
SERVICES=(
    "reddit-crawler:cloud_tasks_reddit.py"
    "news-crawler:cloud_tasks_news.py"
    "coingecko-crawler:cloud_tasks_coingecko.py"
)

# Environment variables for all services
ENV_VARS="NEWSAPI_KEY=ffc45af6fcd94c4991eaefdc469346e8"

echo "📋 Deploying ${#SERVICES[@]} services..."

for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service_name source_file <<< "$service_info"

    echo ""
    echo "🔧 Deploying $service_name..."
    echo "   Source: $source_file"

    # Deploy to Cloud Run
    gcloud run deploy "$service_name" \
        --source . \
        --platform managed \
        --region "$REGION" \
        --project "$PROJECT_ID" \
        --set-env-vars "$ENV_VARS" \
        --memory 1Gi \
        --cpu 1 \
        --max-instances 10 \
        --timeout 300 \
        --concurrency 80 \
        --allow-unauthenticated

    echo "✅ $service_name deployed successfully"
done

echo ""
echo "🎉 All Cloud Tasks deployed successfully!"
echo ""
echo "📊 Deployed Services:"
for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service_name source_file <<< "$service_info"
    echo "   - $service_name"
done

echo ""
echo "🔗 Service URLs:"
for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service_name source_file <<< "$service_info"
    URL=$(gcloud run services describe "$service_name" --region="$REGION" --format="value(status.url)")
    echo "   - $service_name: $URL"
done

echo ""
echo "📝 Next Steps:"
echo "1. Set up Cloud Scheduler jobs to trigger these services"
echo "2. Configure monitoring and alerting"
echo "3. Test each service individually"
echo "4. Verify data is being uploaded to GCS bucket: $BUCKET_NAME"

echo ""
echo "🧪 Test Commands:"
for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service_name source_file <<< "$service_info"
    URL=$(gcloud run services describe "$service_name" --region="$REGION" --format="value(status.url)")
    echo "   curl -X POST $URL"
done

echo ""
echo "✅ Deployment complete!"
