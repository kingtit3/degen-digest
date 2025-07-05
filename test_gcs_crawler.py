#!/usr/bin/env python3
"""
Test script to verify Twitter crawler with GCS upload
"""
import asyncio
import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(".")

from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler


async def test_crawler_with_gcs():
    print("🔍 Testing Twitter Crawler with GCS upload...")

    # Set credentials
    os.environ["TWITTER_USERNAME"] = "gorebroai"
    os.environ["TWITTER_PASSWORD"] = "firefireomg4321"

    # Initialize crawler
    crawler = EnhancedTwitterPlaywrightCrawler(
        headless=True, output_dir="output", cookies_path="output/twitter_cookies.json"
    )
    crawler.current_query = "crypto"

    try:
        # Setup browser
        await crawler.setup_browser()

        # Go to Twitter search for crypto
        search_url = "https://twitter.com/search?q=crypto&src=typed_query&f=live"
        print(f"🔍 Going to: {search_url}")
        await crawler.page.goto(search_url)
        await asyncio.sleep(5)

        # Check if logged in
        try:
            await crawler.page.wait_for_selector(
                "a[data-testid='AppTabBar_Home_Link']", timeout=5000
            )
            print("✅ Logged in with cookies!")

            # Wait for tweets to load
            print("⏳ Waiting for tweets to load...")
            await asyncio.sleep(3)

            # Extract some tweets
            tweets = await crawler.extract_tweets_enhanced(10)
            print(f"Found {len(tweets)} tweets")

            if tweets:
                # Save tweets (should upload to GCS)
                await crawler.save_tweets(tweets)
                print("✅ Tweets saved locally and to GCS!")

                # Show tweet details
                for i, tweet in enumerate(tweets[:3]):
                    text = tweet.get("text", "")[:100]
                    username = tweet.get("username", "unknown")
                    print(f"  Tweet {i+1} by @{username}: {text}...")
            else:
                print("❌ No tweets found")
                # Take a screenshot for debugging
                await crawler.page.screenshot(path="output/debug_no_tweets.png")
                print("📸 Debug screenshot saved to output/debug_no_tweets.png")

        except Exception as e:
            print(f"❌ Not logged in: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await crawler.cleanup()


if __name__ == "__main__":
    asyncio.run(test_crawler_with_gcs())
