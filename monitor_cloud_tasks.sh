#!/bin/bash

# Configuration
PROJECT_ID="lucky-union-463615-t3"
REGION="us-central1"
DEXSCREENER_SERVICE="dexscreener-crawler"
DEXPAPRIKA_SERVICE="dexpaprika-crawler"

echo "🔍 Monitoring Cloud Run Crypto Crawlers..."

# Check Cloud Run services status
echo "📋 Cloud Run Services Status:"
echo "============================="

echo "DexScreener Service:"
gcloud run services describe $DEXSCREENER_SERVICE --region=$REGION --format="table(
    metadata.name,
    status.conditions[0].type,
    status.conditions[0].status,
    status.url
)" 2>/dev/null || echo "Service not found"

echo ""
echo "DexPaprika Service:"
gcloud run services describe $DEXPAPRIKA_SERVICE --region=$REGION --format="table(
    metadata.name,
    status.conditions[0].type,
    status.conditions[0].status,
    status.url
)" 2>/dev/null || echo "Service not found"

# Check Cloud Scheduler jobs
echo ""
echo "⏰ Cloud Scheduler Jobs:"
echo "======================"
gcloud scheduler jobs list --location=$REGION --format="table(
    name,
    schedule,
    state,
    lastAttemptTime
)" 2>/dev/null || echo "No scheduler jobs found"

# Check recent logs
echo ""
echo "📊 Recent Cloud Run Logs (last 20 entries):"
echo "==========================================="
gcloud logging read "resource.type=cloud_run_revision AND (resource.labels.service_name=$DEXSCREENER_SERVICE OR resource.labels.service_name=$DEXPAPRIKA_SERVICE)" \
    --limit=20 \
    --format="table(
        timestamp,
        resource.labels.service_name,
        severity,
        textPayload
    )" 2>/dev/null || echo "No logs found"

# Check GCS files
echo ""
echo "💾 GCS Upload Status:"
echo "===================="
echo "DexScreener files:"
gsutil ls gs://degen-digest-data/data/ | grep dexscreener | tail -5 2>/dev/null || echo "No DexScreener files found"

echo ""
echo "DexPaprika files:"
gsutil ls gs://degen-digest-data/data/ | grep dexpaprika | tail -5 2>/dev/null || echo "No DexPaprika files found"

# Get service URLs for manual testing
echo ""
echo "🎯 Service URLs for Manual Testing:"
echo "==================================="
DEXSCREENER_URL=$(gcloud run services describe $DEXSCREENER_SERVICE --region=$REGION --format="value(status.url)" 2>/dev/null)
DEXPAPRIKA_URL=$(gcloud run services describe $DEXPAPRIKA_SERVICE --region=$REGION --format="value(status.url)" 2>/dev/null)

if [ ! -z "$DEXSCREENER_URL" ]; then
    echo "DexScreener: $DEXSCREENER_URL"
    echo "  Test: curl -X POST $DEXSCREENER_URL"
fi

if [ ! -z "$DEXPAPRIKA_URL" ]; then
    echo "DexPaprika:  $DEXPAPRIKA_URL"
    echo "  Test: curl -X POST $DEXPAPRIKA_URL"
fi

echo ""
echo "📋 Quick Commands:"
echo "=================="
echo "  List services: gcloud run services list --region=$REGION"
echo "  List schedulers: gcloud scheduler jobs list --location=$REGION"
echo "  View logs: gcloud logging read 'resource.type=cloud_run_revision' --limit=50"
echo "  Check GCS: gsutil ls gs://degen-digest-data/data/ | grep -E '(dexscreener|dexpaprika)'"
