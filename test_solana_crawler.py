#!/usr/bin/env python3
"""
Test Solana-focused Twitter crawler
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))


async def test_solana_crawler():
    """Test Solana-focused crawler"""
    try:
        from scrapers.twitter_playwright_enhanced import (
            EnhancedTwitterPlaywrightCrawler,
        )

        print("🌞 Testing Solana-focused Twitter crawler...")

        # Create crawler with credentials
        crawler = EnhancedTwitterPlaywrightCrawler(
            headless=False,  # Set to False to see the browser
            username="gorebroai",
            password="firefireomg4321",
        )

        # Run Solana-focused crawl
        print("🔍 Starting Solana crawl...")
        tweets = await crawler.run_solana_focused_crawl(
            max_for_you_tweets=20,
            max_followed_accounts=10,
            max_tweets_per_user=5,
            max_saved_posts=5,
        )

        print("✅ Solana crawl completed!")
        print(f"📊 Collected {len(tweets)} total tweets")

        # Calculate statistics
        for_you_tweets = [t for t in tweets if t.get("source_type") == "for_you_page"]
        followed_tweets = [
            t for t in tweets if t.get("source_type") == "followed_account"
        ]
        saved_comments = [
            t for t in tweets if t.get("source_type") == "saved_post_comment"
        ]
        discovered_tweets = [
            t for t in tweets if t.get("source_type") == "discovered_user"
        ]

        print(f"🎯 For You page tweets: {len(for_you_tweets)}")
        print(f"👥 Followed account tweets: {len(followed_tweets)}")
        print(f"💾 Saved post comments: {len(saved_comments)}")
        print(f"🔍 Discovered user tweets: {len(discovered_tweets)}")

        if tweets:
            print("\n🐦 Sample tweets:")
            for i, tweet in enumerate(tweets[:3]):
                source_type = tweet.get("source_type", "unknown")
                if source_type == "for_you_page":
                    source_info = "🎯 For You Page"
                elif source_type == "followed_account":
                    source_info = f"👥 @{tweet.get('followed_username', 'Unknown')}"
                elif source_type == "saved_post_comment":
                    source_info = "💾 Saved Comment"
                elif source_type == "discovered_user":
                    source_info = "🔍 Discovered User"
                else:
                    source_info = "🕷️ Playwright"

                print(f"   {i+1}. @{tweet.get('username', 'Unknown')} ({source_info})")
                print(f"      {tweet.get('text', '')[:100]}...")
                print()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_solana_crawler())
