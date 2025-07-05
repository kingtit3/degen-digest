#!/usr/bin/env python3
"""
Test the enhanced Twitter crawler locally
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone

from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler


async def test_enhanced_crawler():
    print("🔍 Testing Enhanced Twitter Crawler...")
    print("📝 This will test login, cookie persistence, and tweet extraction")

    # Set credentials
    os.environ["TWITTER_USERNAME"] = "gorebroai"
    os.environ["TWITTER_PASSWORD"] = "firefireomg4321"

    crawler = EnhancedTwitterPlaywrightCrawler(
        headless=False,
        output_dir="output",  # Show browser for debugging
    )

    try:
        print("🚀 Setting up browser...")
        await crawler.setup_browser()

        print("🔐 Testing login with cookie persistence...")
        login_success = await crawler.login_to_twitter()
        print(f"Login result: {login_success}")

        if login_success:
            print("📱 Going to home page...")
            await crawler.page.goto("https://twitter.com/home")
            await asyncio.sleep(5)

            print("🔍 Extracting tweets...")
            tweets = await crawler.extract_tweets_enhanced(10)
            print(f"✅ Found {len(tweets)} tweets!")

            if tweets:
                print("\n📝 Sample tweets:")
                for i, tweet in enumerate(tweets[:3]):
                    print(f"\nTweet {i+1}:")
                    print(f"  Text: {tweet.get('text', 'No text')[:100]}...")
                    print(f"  Username: {tweet.get('username', 'Unknown')}")
                    print(f"  Engagement: {tweet.get('engagement', {})}")
                    print(f"  Created: {tweet.get('created_at', 'Unknown')}")

                print("\n💾 Testing tweet saving...")
                await crawler.save_tweets(tweets)
                print("✅ Tweets saved successfully!")

                # Check if files were created
                import glob

                output_files = glob.glob("output/twitter_playwright_enhanced_*.json")
                print(f"📁 Found {len(output_files)} output files:")
                for file in output_files[-3:]:  # Show last 3 files
                    print(f"  - {file}")
            else:
                print("❌ No tweets found")
        else:
            print("❌ Login failed")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("🧹 Cleaning up...")
        await crawler.cleanup()
        print("✅ Test complete")


if __name__ == "__main__":
    asyncio.run(test_enhanced_crawler())
