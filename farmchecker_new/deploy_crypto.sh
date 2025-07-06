#!/bin/bash

echo "🚀 Deploying FarmChecker.xyz with Crypto Features to Google Cloud Run..."

# Set project
echo "📋 Setting project to lucky-union-463615-t3..."
gcloud config set project lucky-union-463615-t3

# Build and deploy
echo "🔨 Building and deploying to Cloud Run..."
gcloud run deploy farmchecker-website \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10

echo "✅ Deployment complete!"
echo "🌐 Your website is available at: https://farmchecker-website-6if5kdcbiq-uc.a.run.app"
echo ""
echo "🎯 New Features Added:"
echo "  - Top 10 Crypto Gainers Scrolling Banner"
echo "  - Trending Tokens Section"
echo "  - Market Overview Dashboard"
echo "  - Real-time Crypto Data Integration"
echo "  - Enhanced Engagement Metrics"
echo ""
echo "📊 Crypto Data Sources:"
echo "  - CoinGecko: 70 tokens"
echo "  - DexScreener: 720 tokens"
echo "  - DexPaprika: 30 tokens"
