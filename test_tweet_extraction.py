#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler


async def test_tweet_extraction():
    print("🔍 Testing tweet extraction fix...")

    # Set credentials
    os.environ["TWITTER_USERNAME"] = "gorebroai"
    os.environ["TWITTER_PASSWORD"] = "firefireomg4321"

    crawler = EnhancedTwitterPlaywrightCrawler(headless=False)

    try:
        print("🚀 Setting up browser...")
        await crawler.setup_browser()

        print("🔐 Logging in...")
        login_success = await crawler.login_to_twitter()
        print(f"Login result: {login_success}")

        if login_success:
            print("📱 Going to home page...")
            await crawler.page.goto("https://twitter.com/home")
            await asyncio.sleep(5)

            print("🔍 Extracting tweets...")
            tweets = await crawler.extract_tweets_enhanced(5)
            print(f"✅ Found {len(tweets)} tweets!")

            if tweets:
                print("\n📝 Sample tweets:")
                for i, tweet in enumerate(tweets[:2]):
                    print(f"\nTweet {i+1}:")
                    print(f"  Text: {tweet.get('text', 'No text')[:100]}...")
                    print(f"  Username: {tweet.get('username', 'Unknown')}")
                    print(f"  Engagement: {tweet.get('engagement', {})}")
            else:
                print("❌ Still no tweets found")
        else:
            print("❌ Login failed")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await crawler.cleanup()


if __name__ == "__main__":
    asyncio.run(test_tweet_extraction())
