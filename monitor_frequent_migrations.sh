#!/bin/bash

echo "📊 Monitoring Frequent Migration System"
echo "======================================"

# Configuration
JOB_NAME="frequent-migration-scheduler"
REGION="us-central1"
SERVICE_URL="https://migration-service-6if5kdcbiq-uc.a.run.app"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}$1${NC}"
}

echo ""
print_info "🔍 Checking Scheduler Status..."

# Check scheduler job status
SCHEDULER_STATUS=$(gcloud scheduler jobs describe $JOB_NAME --location=$REGION --format="value(state)")

if [[ $SCHEDULER_STATUS == "ENABLED" ]]; then
    print_status "✅ Scheduler is ENABLED and running"
else
    print_error "❌ Scheduler is $SCHEDULER_STATUS"
fi

echo ""
print_info "🏥 Checking Service Health..."

# Check service health
HEALTH_RESPONSE=$(curl -s "$SERVICE_URL/health")

if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    print_status "✅ Migration service is healthy"
else
    print_error "❌ Migration service is unhealthy"
    echo "Response: $HEALTH_RESPONSE"
fi

echo ""
print_info "📈 Checking Recent Database Activity..."

# Check recent data collections
RECENT_COLLECTIONS=$(PGPASSWORD='DegenDigest2024!' psql -h 34.9.71.174 -U postgres -d degen_digest -t -c "SELECT COUNT(*) FROM data_collections WHERE collection_timestamp > NOW() - INTERVAL '1 hour';" 2>/dev/null)

if [[ $RECENT_COLLECTIONS -gt 0 ]]; then
    print_status "✅ Found $RECENT_COLLECTIONS recent data collections (last hour)"
else
    print_warning "⚠️  No recent data collections found in the last hour"
fi

echo ""
print_info "📊 Current Database Status..."

# Get current data counts
PGPASSWORD='DegenDigest2024!' psql -h 34.9.71.174 -U postgres -d degen_digest -c "SELECT ds.name, COUNT(*) as item_count FROM data_sources ds LEFT JOIN content_items ci ON ds.id = ci.source_id GROUP BY ds.name ORDER BY item_count DESC;" 2>/dev/null

echo ""
print_info "🕐 Next Scheduled Runs..."

# Show next few scheduled times
echo "Based on */10 * * * * schedule:"
for i in {0..5}; do
    NEXT_TIME=$(date -v+${i}0M "+%H:%M" 2>/dev/null || date -d "+$((i*10)) minutes" "+%H:%M" 2>/dev/null || echo "XX:XX")
    echo "   • $NEXT_TIME"
done

echo ""
print_info "🔧 Management Commands:"

echo "   View scheduler details:"
echo "   gcloud scheduler jobs describe $JOB_NAME --location=$REGION"
echo ""
echo "   Pause frequent migrations:"
echo "   gcloud scheduler jobs pause $JOB_NAME --location=$REGION"
echo ""
echo "   Resume frequent migrations:"
echo "   gcloud scheduler jobs resume $JOB_NAME --location=$REGION"
echo ""
echo "   Manual migration trigger:"
echo "   ./trigger_migration.sh"
echo ""
echo "   View Cloud Run logs:"
echo "   gcloud logs read 'resource.type=cloud_run_revision AND resource.labels.service_name=migration-service' --limit=20"

echo ""
print_warning "💡 Tips:"
echo "   • Monitor Cloud Run costs with frequent executions"
echo "   • Check logs if migrations seem to be failing"
echo "   • Consider pausing during maintenance windows"
echo "   • Database uses ON CONFLICT DO NOTHING to prevent duplicates"

echo ""
print_status "🎉 Frequent migration system is active and monitoring!"
