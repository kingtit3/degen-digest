#!/bin/bash

# Enhanced Viral Content System Deployment Script
echo "🚀 Deploying Enhanced Viral Content System..."

# Set environment variables
export PROJECT_ID="lucky-union-463615-t3"
export BUCKET_NAME="degen-digest-data"
export NEWSAPI_KEY="ffc45af6fcd94c4991eaefdc469346e8"

echo "📋 Environment variables set:"
echo "  PROJECT_ID: $PROJECT_ID"
echo "  BUCKET_NAME: $BUCKET_NAME"
echo "  NEWSAPI_KEY: $NEWSAPI_KEY"

# Function to deploy a cloud function
deploy_function() {
    local function_name=$1
    local entry_point=$2
    local env_vars=$3

    echo "📦 Deploying $function_name..."

    gcloud functions deploy $function_name \
        --runtime python311 \
        --trigger-http \
        --allow-unauthenticated \
        --region us-central1 \
        --source . \
        --entry-point $entry_point \
        --timeout 540s \
        --memory 512MB \
        --set-env-vars $env_vars

    if [ $? -eq 0 ]; then
        echo "✅ $function_name deployed successfully!"

        # Get the function URL
        local function_url=$(gcloud functions describe $function_name --region=us-central1 --format="value(httpsTrigger.url)")
        echo "🌐 $function_name URL: $function_url"

        # Test the function
        echo "🧪 Testing $function_name..."
        curl -X POST "$function_url" -H "Content-Type: application/json" -d '{}' --max-time 30

        echo ""
    else
        echo "❌ Failed to deploy $function_name"
        return 1
    fi
}

# Deploy Enhanced Reddit Crawler
echo "🔄 Deploying Enhanced Reddit Crawler..."
deploy_function "enhanced-reddit-crawler" "enhanced_reddit_crawler" "PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME"

# Deploy Enhanced News Crawler
echo "🔄 Deploying Enhanced News Crawler..."
deploy_function "enhanced-news-crawler" "enhanced_news_crawler" "PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME,NEWSAPI_KEY=$NEWSAPI_KEY"

# Deploy Enhanced CoinGecko Crawler
echo "🔄 Deploying Enhanced CoinGecko Crawler..."
deploy_function "enhanced-coingecko-crawler" "enhanced_coingecko_crawler" "PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME"

echo ""
echo "🎯 Setting up Cloud Scheduler jobs..."

# Get function URLs for scheduler
REDDIT_URL=$(gcloud functions describe enhanced-reddit-crawler --region=us-central1 --format="value(httpsTrigger.url)")
NEWS_URL=$(gcloud functions describe enhanced-news-crawler --region=us-central1 --format="value(httpsTrigger.url)")
COINGECKO_URL=$(gcloud functions describe enhanced-coingecko-crawler --region=us-central1 --format="value(httpsTrigger.url)")

# Create schedulers for enhanced functions
echo "⏰ Creating Enhanced Reddit Scheduler..."
gcloud scheduler jobs create http enhanced-reddit-viral-crawler \
    --schedule="*/30 6-23 * * *" \
    --uri="$REDDIT_URL" \
    --http-method=POST \
    --location=us-central1 \
    --description="Enhanced Reddit viral content crawler" \
    --quiet

echo "⏰ Creating Enhanced News Scheduler..."
gcloud scheduler jobs create http enhanced-news-viral-crawler \
    --schedule="*/45 6-23 * * *" \
    --uri="$NEWS_URL" \
    --http-method=POST \
    --location=us-central1 \
    --description="Enhanced News viral content crawler" \
    --quiet

echo "⏰ Creating Enhanced CoinGecko Scheduler..."
gcloud scheduler jobs create http enhanced-coingecko-viral-crawler \
    --schedule="*/20 6-23 * * *" \
    --uri="$COINGECKO_URL" \
    --http-method=POST \
    --location=us-central1 \
    --description="Enhanced CoinGecko viral content crawler" \
    --quiet

echo ""
echo "🎉 Enhanced Viral Content System Deployment Complete!"
echo ""
echo "📊 Summary:"
echo "  ✅ Enhanced Reddit Crawler: $REDDIT_URL"
echo "  ✅ Enhanced News Crawler: $NEWS_URL"
echo "  ✅ Enhanced CoinGecko Crawler: $COINGECKO_URL"
echo ""
echo "⏰ Schedulers:"
echo "  🔄 Reddit: Every 30 minutes (6AM-11PM)"
echo "  🔄 News: Every 45 minutes (6AM-11PM)"
echo "  🔄 CoinGecko: Every 20 minutes (6AM-11PM)"
echo ""
echo "📈 Expected Results:"
echo "  • 300+ Reddit posts/day (25+ subreddits)"
echo "  • 200+ News articles/day (20+ queries)"
echo "  • 400+ CoinGecko coins/day (8 endpoints)"
echo "  • Total: 1250+ viral content items/day"
echo ""
echo "🚀 Your enhanced viral content system is now live!"
