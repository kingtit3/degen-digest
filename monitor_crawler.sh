#!/bin/bash

# Monitor Continuous Solana Crawler on Google Cloud

PROJECT_ID="lucky-union-463615-t3"
REGION="us-central1"
SERVICE_NAME="solana-crawler"

echo "🔍 Monitoring Continuous Solana Crawler..."

echo "📊 Monitoring Solana Crawler Status"
echo "=================================="

# Check service status
echo "📋 Service Status:"
gcloud compute ssh king@solana-crawler-vm --zone=us-central1-a --command='sudo systemctl status continuous-solana-crawler.service --no-pager'

echo ""

# Check recent logs
echo "📊 Recent Logs (last 20 entries):"
gcloud compute ssh king@solana-crawler-vm --zone=us-central1-a --command='sudo journalctl -u continuous-solana-crawler.service -n 20 --no-pager'

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

echo ""
echo "📁 Recent Output Files:"
gcloud compute ssh king@solana-crawler-vm --zone=us-central1-a --command='ls -la ~/DegenDigest/output/ | tail -10'

echo ""
echo "💾 GCS Upload Status:"
gcloud compute ssh king@solana-crawler-vm --zone=us-central1-a --command='cd ~/DegenDigest && python3 -c "from scrapers.solana_playwright_enhanced import EnhancedSolanaPlaywrightCrawler; import asyncio; async def check(): crawler = EnhancedSolanaPlaywrightCrawler(); print(\"✅ GCS connection working\"); asyncio.run(check())" 2>/dev/null || echo "❌ GCS connection issue"

echo ""
echo "🎯 Quick Commands:"
echo "  Start: gcloud compute ssh king@solana-crawler-vm --zone=us-central1-a --command='sudo systemctl start continuous-solana-crawler.service'"
echo "  Stop:  gcloud compute ssh king@solana-crawler-vm --zone=us-central1-a --command='sudo systemctl stop continuous-solana-crawler.service'"
echo "  Logs:  gcloud compute ssh king@solana-crawler-vm --zone=us-central1-a --command='sudo journalctl -u continuous-solana-crawler.service -f'"
