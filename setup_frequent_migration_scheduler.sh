#!/bin/bash

echo "🕐 Setting up Frequent Migration Scheduler (Every 10 Minutes)"
echo "============================================================"

# Configuration
JOB_NAME="frequent-migration-scheduler"
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

print_status "🔧 Creating frequent migration scheduler job..."

# Create the scheduler job that runs every 10 minutes
gcloud scheduler jobs create http $JOB_NAME \
    --schedule="*/10 * * * *" \
    --uri="$SERVICE_URL/migrate" \
    --http-method=POST \
    --location=$REGION \
    --project=$PROJECT_ID \
    --description="Frequent data migration every 10 minutes for real-time crypto updates" \
    --time-zone="UTC" \
    --attempt-deadline="300s"

if [ $? -eq 0 ]; then
    print_status "✅ Frequent migration scheduler created successfully!"
    echo ""
    print_status "📅 Schedule: Every 10 minutes (*/10 * * * *)"
    print_status "🔗 Service URL: $SERVICE_URL/migrate"
    print_status "⏰ Timezone: UTC"
    print_status "⏱️  Timeout: 5 minutes per attempt"
    echo ""
    print_status "📊 Expected frequency:"
    echo "   • 6 times per hour"
    echo "   • 144 times per day"
    echo "   • Real-time crypto data updates"
    echo ""
    print_status "🔧 To manage the scheduler:"
    echo "   View jobs: gcloud scheduler jobs list --location=$REGION"
    echo "   Pause job: gcloud scheduler jobs pause $JOB_NAME --location=$REGION"
    echo "   Resume job: gcloud scheduler jobs resume $JOB_NAME --location=$REGION"
    echo "   Delete job: gcloud scheduler jobs delete $JOB_NAME --location=$REGION"
    echo ""
    print_status "📈 Monitor execution:"
    echo "   gcloud scheduler jobs describe $JOB_NAME --location=$REGION"
    echo ""
    print_warning "⚠️  Note: This will run 144 times per day. Monitor your Cloud Run costs."
    echo ""
    print_status "🎉 Frequent migration automation is now set up!"

else
    print_error "❌ Failed to create frequent migration scheduler!"
    exit 1
fi
