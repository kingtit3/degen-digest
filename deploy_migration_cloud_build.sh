#!/bin/bash

echo "🚀 Deploying Migration Service via Cloud Build"
echo "============================================="

# Set variables
SERVICE_NAME="migration-service"
REGION="us-central1"
PROJECT_ID="lucky-union-463615-t3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# Check if we're in the right directory
if [ ! -d "migration_service" ]; then
    print_error "❌ migration_service directory not found!"
    exit 1
fi

print_status "🔧 Building and deploying with Cloud Build..."

# Deploy using Cloud Build
gcloud run deploy $SERVICE_NAME \
    --source=migration_service \
    --platform=managed \
    --region=$REGION \
    --project=$PROJECT_ID \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=900 \
    --max-instances=1 \
    --min-instances=0 \
    --port=8080 \
    --set-env-vars="DB_HOST=34.9.71.174,DB_PORT=5432,DB_NAME=degen_digest,DB_USER=postgres,DB_PASSWORD=DegenDigest2024!,BUCKET_NAME=degen-digest-data,PROJECT_ID=$PROJECT_ID" \
    --concurrency=1 \
    --execution-environment=gen2

if [ $? -eq 0 ]; then
    print_status "✅ Migration service deployed successfully!"

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

    echo ""
    print_status "🔗 Service URL: $SERVICE_URL"
    echo ""
    print_status "🔧 Available endpoints:"
    echo "   Health check: $SERVICE_URL/health"
    echo "   Migration: $SERVICE_URL/migrate (POST)"
    echo ""
    print_status "🧪 Testing health endpoint..."

    # Test the health endpoint
    sleep 15  # Wait for service to be ready
    HEALTH_RESPONSE=$(curl -s "$SERVICE_URL/health")

    if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
        print_status "✅ Health check passed!"
        echo ""
        print_status "🎉 Service is ready for use!"
        echo ""
        print_status "To run migration:"
        echo "curl -X POST $SERVICE_URL/migrate"
    else
        print_warning "⚠️  Health check failed. Service might still be starting up."
        echo "Response: $HEALTH_RESPONSE"
    fi

else
    print_error "❌ Cloud Run deployment failed!"
    exit 1
fi
