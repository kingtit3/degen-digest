#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler


async def test_login():
    crawler = EnhancedTwitterPlaywrightCrawler()
    try:
        print("Setting up browser...")
        await crawler.setup_browser()

        print("Testing login...")
        success = await crawler.login_to_twitter()
        print(f"Login result: {success}")

        if success:
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await crawler.cleanup()


if __name__ == "__main__":
    asyncio.run(test_login())
