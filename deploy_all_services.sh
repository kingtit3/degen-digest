#!/bin/bash

echo "🚀 Deploying All Degen Digest Services..."
echo "=========================================="

# Deploy Reddit Crawler
echo ""
echo "📱 Deploying Reddit Crawler..."
./deploy_reddit_crawler.sh

# Deploy Crypto Crawler
echo ""
echo "💰 Deploying Crypto Crawler..."
./deploy_crypto_crawler.sh

# Deploy News Crawler
echo ""
echo "📰 Deploying News Crawler..."
./deploy_news_crawler.sh

# Deploy Twitter Crawler
echo ""
echo "🐦 Deploying Twitter Crawler..."
./deploy_twitter_crawler.sh

# Deploy Data Aggregator
echo ""
echo "🔗 Deploying Data Aggregator..."
./deploy_data_aggregator.sh

echo ""
echo "✅ All services deployed!"
echo ""
echo "🌐 Service URLs:"
echo "  - Reddit Crawler: https://reddit-crawler-128671663649.us-central1.run.app"
echo "  - Crypto Crawler: https://crypto-crawler-128671663649.us-central1.run.app"
echo "  - News Crawler: https://news-crawler-128671663649.us-central1.run.app"
echo "  - Twitter Crawler: https://twitter-crawler-128671663649.us-central1.run.app"
echo "  - Data Aggregator: https://data-aggregator-128671663649.us-central1.run.app"
echo ""
echo "⚠️  Next Steps:"
echo "  1. Set TWITTER_USERNAME and TWITTER_PASSWORD for Twitter Crawler"
echo "  2. Set NEWSAPI_KEY for News Crawler (if needed)"
echo "  3. Test each service individually"
echo "  4. Set up Cloud Scheduler to trigger services"
echo "  5. Monitor logs for each service"
