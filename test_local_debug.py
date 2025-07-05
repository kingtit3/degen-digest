#!/usr/bin/env python3
"""
Local debug script for Twitter crawler - runs in headful mode for visual debugging
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler


async def debug_crawler():
    print("🔍 Starting local debug mode...")
    print("📝 This will open a browser window so you can see what's happening")
    print(
        "🔑 Make sure TWITTER_USERNAME and TWITTER_PASSWORD are set in your environment"
    )

    # Set credentials if not already set
    if not os.getenv("TWITTER_USERNAME"):
        os.environ["TWITTER_USERNAME"] = "gorebroai"
    if not os.getenv("TWITTER_PASSWORD"):
        os.environ["TWITTER_PASSWORD"] = "firefireomg4321"

    crawler = EnhancedTwitterPlaywrightCrawler(
        headless=False,
        output_dir="output",  # Show browser window
    )

    try:
        print("🚀 Setting up browser (headful mode)...")
        await crawler.setup_browser()

        print("🔐 Attempting to login to Twitter...")
        print("   Username:", os.getenv("TWITTER_USERNAME"))
        print(
            "   Password:",
            "***" + os.getenv("TWITTER_PASSWORD")[-4:]
            if os.getenv("TWITTER_PASSWORD")
            else "Not set",
        )

        login_success = await crawler.login_to_twitter()
        print(f"Login result: {login_success}")

        if login_success:
            print("✅ Login successful! Now testing tweet extraction...")

            # Test For You page
            print("📱 Navigating to For You page...")
            await crawler.page.goto("https://twitter.com/home")
            await asyncio.sleep(5)

            print("🔍 Extracting tweets from For You page...")
            tweets = await crawler.extract_tweets_enhanced(5)
            print(f"Found {len(tweets)} tweets from For You page")

            if tweets:
                for i, tweet in enumerate(tweets[:3]):
                    print(f"\nTweet {i+1}:")
                    print(f"  Text: {tweet.get('text', 'No text')[:100]}...")
                    print(f"  Username: {tweet.get('username', 'Unknown')}")
                    print(f"  Engagement: {tweet.get('engagement', {})}")
            else:
                print("❌ No tweets found - this indicates a selector issue")

                # Debug: Take a screenshot
                print("📸 Taking screenshot for debugging...")
                await crawler.page.screenshot(path="debug_screenshot.png")
                print("Screenshot saved as debug_screenshot.png")

                # Debug: Check page content
                print("🔍 Checking page content...")
                page_content = await crawler.page.content()
                if "tweet" in page_content.lower():
                    print("✅ 'tweet' found in page content")
                else:
                    print("❌ 'tweet' not found in page content")

        else:
            print("❌ Login failed - check credentials and try again")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("🧹 Cleaning up...")
        await crawler.cleanup()
        print("✅ Debug session complete")


if __name__ == "__main__":
    asyncio.run(debug_crawler())
