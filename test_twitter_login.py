#!/usr/bin/env python3
"""
Test Twitter login with provided credentials
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))


async def test_twitter_login():
    """Test Twitter login with provided credentials"""
    try:
        from scrapers.twitter_playwright_enhanced import (
            EnhancedTwitterPlaywrightCrawler,
        )

        print("🔐 Testing Twitter login...")

        # Create crawler with credentials
        crawler = EnhancedTwitterPlaywrightCrawler(
            headless=False,  # Set to False to see the browser
            username="gorebroai",
            password="firefireomg4321",
        )

        # Test login
        await crawler.setup_browser()
        login_success = await crawler.login_to_twitter()

        if login_success:
            print("✅ Login successful!")

            # Test a quick search
            print("🔍 Testing search...")
            tweets = await crawler.search_twitter("bitcoin", max_tweets=5)
            print(f"📊 Found {len(tweets)} tweets")

            if tweets:
                print("🐦 Sample tweet:")
                print(f"   User: @{tweets[0].get('username', 'Unknown')}")
                print(f"   Text: {tweets[0].get('text', '')[:100]}...")

        else:
            print("❌ Login failed")

        await crawler.cleanup()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_twitter_login())
