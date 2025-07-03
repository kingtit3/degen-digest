#!/bin/bash

# Monitor Continuous Solana Crawler on Google Cloud

PROJECT_ID="lucky-union-463615-t3"
REGION="us-central1"
SERVICE_NAME="solana-crawler"

echo "📊 Monitoring Solana Crawler Status"
echo "=================================="

# Check service status
echo "🔍 Service Status:"
gcloud run services describe $SERVICE_NAME --region=$REGION --format="table(
    metadata.name,
    status.conditions[0].type,
    status.conditions[0].status,
    status.url
)" || echo "Service not found or not accessible"

echo ""

# Check recent logs
echo "📝 Recent Logs (last 20 entries):"
gcloud logs read --service=$SERVICE_NAME --region=$REGION --limit=20 --format="table(
    timestamp,
    severity,
    textPayload
)" || echo "No logs found"

echo ""

# Check resource usage
echo "💾 Resource Usage:"
gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(
    spec.template.spec.containers[0].resources.limits.memory,
    spec.template.spec.containers[0].resources.limits.cpu
)" || echo "Resource info not available"

echo ""

# Check if service is running
echo "🔄 Service Health:"
gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.conditions[0].status)" 2>/dev/null | grep -q "True" && echo "✅ Service is running" || echo "❌ Service is not running"

echo ""
echo "🔗 To view full logs:"
echo "   gcloud logs read --service=$SERVICE_NAME --region=$REGION --limit=100"
echo ""
echo "🛑 To stop the crawler:"
echo "   gcloud run services delete $SERVICE_NAME --region=$REGION"
