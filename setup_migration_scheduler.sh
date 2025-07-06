#!/bin/bash

echo "🕐 Setting up Migration Scheduler"
echo "================================"

# Configuration
JOB_NAME="migration-scheduler"
REGION="us-central1"
PROJECT_ID="lucky-union-463615-t3"
SERVICE_URL="https://migration-service-6if5kdcbiq-uc.a.run.app"

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

print_status "🔧 Creating Cloud Scheduler job..."

# Create the scheduler job
gcloud scheduler jobs create http $JOB_NAME \
    --schedule="0 */6 * * *" \
    --uri="$SERVICE_URL/migrate" \
    --http-method=POST \
    --location=$REGION \
    --project=$PROJECT_ID \
    --description="Automated data migration every 6 hours" \
    --time-zone="UTC"

if [ $? -eq 0 ]; then
    print_status "✅ Scheduler job created successfully!"
    echo ""
    print_status "📅 Schedule: Every 6 hours (0 */6 * * *)"
    print_status "🔗 Service URL: $SERVICE_URL/migrate"
    print_status "⏰ Timezone: UTC"
    echo ""
    print_status "🔧 To manage the scheduler:"
    echo "   View jobs: gcloud scheduler jobs list --location=$REGION"
    echo "   Pause job: gcloud scheduler jobs pause $JOB_NAME --location=$REGION"
    echo "   Resume job: gcloud scheduler jobs resume $JOB_NAME --location=$REGION"
    echo "   Delete job: gcloud scheduler jobs delete $JOB_NAME --location=$REGION"
    echo ""
    print_status "🎉 Migration automation is now set up!"

else
    print_error "❌ Failed to create scheduler job!"
    exit 1
fi
