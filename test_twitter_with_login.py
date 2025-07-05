#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler


async def test_with_login():
    crawler = EnhancedTwitterPlaywrightCrawler()
    try:
        print("Setting up browser...")
        await crawler.setup_browser()

        print("Attempting to login to Twitter...")
        login_success = await crawler.login_to_twitter()

        if login_success:
            print("✅ Login successful!")

            print("Navigating to For You page...")
            await crawler.page.goto("https://twitter.com/home")
            await asyncio.sleep(10)

            print("Extracting tweets from For You page...")
            tweets = await crawler.extract_tweets_enhanced(10)

            print(f"Found {len(tweets)} tweets from For You page")
            for i, tweet in enumerate(tweets[:3]):
                print(f"Tweet {i+1}: {tweet.get('text', 'No text')[:100]}...")
                print(f"  Username: {tweet.get('username', 'Unknown')}")
                print(f"  Engagement: {tweet.get('engagement', {})}")
        else:
            print("❌ Login failed!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await crawler.cleanup()


if __name__ == "__main__":
    asyncio.run(test_with_login())
