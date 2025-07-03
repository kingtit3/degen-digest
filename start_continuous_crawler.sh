#!/bin/bash

# Continuous Solana Crawler Startup Script
# Runs 18 hours a day (6 AM to 12 AM)

echo "🚀 Starting Continuous Solana Twitter Crawler"
echo "📅 Schedule: 6 AM - 12 AM (18 hours daily)"
echo "⏰ Crawl interval: 30 minutes (randomized)"
echo ""

# Create logs directory
mkdir -p logs

# Start the continuous crawler
python3 scripts/continuous_solana_crawler.py \
    --username "gorebroai" \
    --password "firefireomg4321" \
    --start-hour 6 \
    --end-hour 0 \
    --interval 30

echo "�� Crawler stopped"
