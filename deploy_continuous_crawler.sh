#!/bin/bash

echo "🚀 Deploying Continuous Twitter Crawler to VM..."

# Upload files to VM
echo "📤 Uploading files to VM..."
gcloud compute scp continuous_twitter_crawler.py king@twitter-crawler-vm:~/DegenDigest/ --zone=us-central1-a
gcloud compute scp continuous-twitter-crawler.service king@twitter-crawler-vm:~/DegenDigest/ --zone=us-central1-a

# Setup service on VM
echo "🔧 Setting up systemd service on VM..."
gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a --command="cd ~/DegenDigest && mkdir -p output && sudo cp continuous-twitter-crawler.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable continuous-twitter-crawler.service"

echo "✅ Service setup completed!"
echo ""
echo "🎯 Next steps:"
echo "1. SSH to VM: gcloud compute ssh king@twitter-crawler-vm --zone=us-central1-a"
echo "2. Start service: sudo systemctl start continuous-twitter-crawler.service"
echo "3. Monitor logs: sudo journalctl -u continuous-twitter-crawler.service -f"
echo "4. Check status: sudo systemctl status continuous-twitter-crawler.service"
