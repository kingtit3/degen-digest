#!/usr/bin/env python3
"""
Test script for Playwright Twitter Crawler
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from scrapers.twitter_playwright import TwitterPlaywrightCrawler


async def test_single_search():
    """Test a single search query"""
    print("🧪 Testing Playwright Twitter Crawler...")

    crawler = TwitterPlaywrightCrawler(headless=True)

    try:
        await crawler.setup_browser()
        print("✅ Browser setup successful")

        # Test with a single query
        tweets = await crawler.search_twitter("bitcoin", max_tweets=5)

        print(f"📊 Found {len(tweets)} tweets")

        if tweets:
            print("\n📝 Sample tweet:")
            sample = tweets[0]
            print(f"   Text: {sample['text'][:100]}...")
            print(f"   Username: {sample['username']}")
            print(f"   Sentiment: {sample['sentiment']}")
            print(f"   Engagement: {sample['engagement']}")

        # Save test results
        await crawler.save_tweets(tweets)

        print("✅ Test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await crawler.cleanup()


async def test_continuous_crawl():
    """Test continuous crawling for a short period"""
    print("🔄 Testing continuous crawl (will run for 2 minutes)...")

    crawler = TwitterPlaywrightCrawler(headless=True)

    try:
        # Run for just 2 minutes to test
        await crawler.crawl_continuously(interval_minutes=1, max_tweets_per_query=3)
    except KeyboardInterrupt:
        print("⏹️ Continuous crawl stopped by user")
    except Exception as e:
        print(f"❌ Continuous crawl failed: {e}")
    finally:
        await crawler.cleanup()


def main():
    """Main test function"""
    print("🚀 Playwright Twitter Crawler Test")
    print("=" * 50)

    # Test single search
    asyncio.run(test_single_search())

    print("\n" + "=" * 50)

    # Ask if user wants to test continuous crawl
    response = input("Test continuous crawl? (y/n): ").lower().strip()
    if response == "y":
        print("\n🔄 Starting continuous crawl test...")
        print("Press Ctrl+C to stop")
        asyncio.run(test_continuous_crawl())


if __name__ == "__main__":
    main()
