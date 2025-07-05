#!/bin/bash

echo "🚀 Deploying Continuous Crypto Crawlers (DexScreener & DexPaprika) to VM..."

# Upload files to VM
echo "📤 Uploading files to VM..."
gcloud compute scp continuous_dexscreener_crawler.py king@twitter-crawler-vm:~/DegenDigest/ --zone=us-central1-a
gcloud compute scp continuous_dexpaprika_crawler.py king@twitter-crawler-vm:~/DegenDigest/ --zone=us-central1-a
gcloud compute scp continuous-dexscreener-crawler.service king@twitter-crawler-vm:~/DegenDigest/ --zone=us-central1-a
gcloud compute scp continuous-dexpaprika-crawler.service king@twitter-crawler-vm:~/DegenDigest/ --zone=us-central1-a

# Setup services on VM
echo "🔧 Setting up systemd services on VM..."
gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command="cd ~/DegenDigest && mkdir -p output && sudo cp continuous-dexscreener-crawler.service /etc/systemd/system/ && sudo cp continuous-dexpaprika-crawler.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable continuous-dexscreener-crawler.service && sudo systemctl enable continuous-dexpaprika-crawler.service"

echo "✅ Services setup completed!"
echo ""
echo "🎯 Next steps:"
echo "1. SSH to VM: gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a"
echo "2. Start DexScreener: sudo systemctl start continuous-dexscreener-crawler.service"
echo "3. Start DexPaprika: sudo systemctl start continuous-dexpaprika-crawler.service"
echo "4. Check status: sudo systemctl status continuous-dexscreener-crawler.service"
echo "5. Check status: sudo systemctl status continuous-dexpaprika-crawler.service"
echo "6. Monitor logs: sudo journalctl -u continuous-dexscreener-crawler.service -f"
echo "7. Monitor logs: sudo journalctl -u continuous-dexpaprika-crawler.service -f"
