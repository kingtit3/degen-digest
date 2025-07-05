#!/bin/bash

echo "🔍 Monitoring Continuous Crypto Crawlers (DexScreener & DexPaprika)..."

# Check DexScreener service status
echo "📋 DexScreener Service Status:"
gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo systemctl status continuous-dexscreener-crawler.service --no-pager'

echo ""
echo "📋 DexPaprika Service Status:"
gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo systemctl status continuous-dexpaprika-crawler.service --no-pager'

echo ""
echo "📊 Recent DexScreener Logs (last 20 lines):"
gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo journalctl -u continuous-dexscreener-crawler.service -n 20 --no-pager'

echo ""
echo "📊 Recent DexPaprika Logs (last 20 lines):"
gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo journalctl -u continuous-dexpaprika-crawler.service -n 20 --no-pager'

echo ""
echo "📁 Recent Output Files:"
gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='ls -la ~/DegenDigest/output/ | grep -E "(dexscreener|dexpaprika)" | tail -10'

echo ""
echo "💾 GCS Upload Status:"
gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='cd ~/DegenDigest && python3 -c "from google.cloud import storage; client = storage.Client(); bucket = client.bucket(\"degen-digest-data\"); blobs = list(bucket.list_blobs(prefix=\"data/dexscreener\")); print(f\"DexScreener files in GCS: {len(blobs)}\"); blobs = list(bucket.list_blobs(prefix=\"data/dexpaprika\")); print(f\"DexPaprika files in GCS: {len(blobs)}\")" 2>/dev/null || echo "❌ GCS connection issue"'

echo ""
echo "🎯 Quick Commands:"
echo "  Start DexScreener: gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo systemctl start continuous-dexscreener-crawler.service'"
echo "  Start DexPaprika:  gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo systemctl start continuous-dexpaprika-crawler.service'"
echo "  Stop DexScreener:  gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo systemctl stop continuous-dexscreener-crawler.service'"
echo "  Stop DexPaprika:   gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo systemctl stop continuous-dexpaprika-crawler.service'"
echo "  DexScreener Logs:  gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo journalctl -u continuous-dexscreener-crawler.service -f'"
echo "  DexPaprika Logs:   gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command='sudo journalctl -u continuous-dexpaprika-crawler.service -f'"
