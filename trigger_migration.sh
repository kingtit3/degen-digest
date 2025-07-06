#!/bin/bash

echo "🚀 Triggering Cloud Run Migration"
echo "================================="

# Service URL
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

print_status "🔍 Checking service health..."

# Check health first
HEALTH_RESPONSE=$(curl -s "$SERVICE_URL/health")

if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    print_status "✅ Service is healthy"
else
    print_error "❌ Service is unhealthy"
    echo "Response: $HEALTH_RESPONSE"
    exit 1
fi

print_status "🚀 Triggering migration..."

# Trigger migration
MIGRATION_RESPONSE=$(curl -s -X POST "$SERVICE_URL/migrate")

if [[ $MIGRATION_RESPONSE == *"success"* ]]; then
    print_status "✅ Migration completed successfully!"

    # Parse and display results
    TOTAL_IMPORTED=$(echo $MIGRATION_RESPONSE | grep -o '"total_imported":[0-9]*' | cut -d':' -f2)
    print_status "📊 Total items imported: $TOTAL_IMPORTED"

    # Extract source stats
    echo ""
    print_status "📈 Breakdown by source:"
    echo $MIGRATION_RESPONSE | grep -o '"source_stats":{[^}]*}' | sed 's/"source_stats":{//' | sed 's/}//' | tr ',' '\n' | sed 's/"//g' | sed 's/:/: /' | while read line; do
        if [[ $line == *":"* ]]; then
            echo "   $line items"
        fi
    done

    echo ""
    print_status "🎉 Migration completed successfully!"

else
    print_error "❌ Migration failed!"
    echo "Response: $MIGRATION_RESPONSE"
    exit 1
fi
