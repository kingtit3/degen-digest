#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler


async def test_simple_search():
    crawler = EnhancedTwitterPlaywrightCrawler()
    try:
        print("Setting up browser...")
        await crawler.setup_browser()

        print("Navigating to Twitter search...")
        await crawler.page.goto(
            "https://twitter.com/search?q=solana&src=typed_query&f=live"
        )

        print("Waiting for page to load...")
        await asyncio.sleep(15)

        print("Extracting tweets...")
        tweets = await crawler.extract_tweets_enhanced(5)

        print(f"Found {len(tweets)} tweets")
        for i, tweet in enumerate(tweets[:3]):
            print(f"Tweet {i+1}: {tweet.get('text', 'No text')[:100]}...")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await crawler.cleanup()


if __name__ == "__main__":
    asyncio.run(test_simple_search())
