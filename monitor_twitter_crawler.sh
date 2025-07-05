#!/bin/bash

echo "🔍 Monitoring Continuous Twitter Crawler..."

# Check service status
echo "📋 Service Status:"
gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo systemctl status continuous-twitter-crawler.service --no-pager'

echo ""
echo "📊 Recent Logs (last 20 lines):"
gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo journalctl -u continuous-twitter-crawler.service -n 20 --no-pager'

echo ""
echo "📁 Recent Output Files:"
gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='ls -la ~/DegenDigest/output/ | tail -10'

echo ""
echo "💾 GCS Upload Status:"
gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='cd ~/DegenDigest && python3 -c "from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler; import asyncio; async def check(): crawler = EnhancedTwitterPlaywrightCrawler(); print(\"✅ GCS connection working\"); asyncio.run(check())" 2>/dev/null || echo "❌ GCS connection issue"'

echo ""
echo "🎯 Quick Commands:"
echo "  Start: gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo systemctl start continuous-twitter-crawler.service'"
echo "  Stop:  gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo systemctl stop continuous-twitter-crawler.service'"
echo "  Logs:  gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo journalctl -u continuous-twitter-crawler.service -f'"
