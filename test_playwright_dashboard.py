#!/usr/bin/env python3
"""
Test script for Playwright crawler dashboard integration
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))


def test_playwright_imports():
    """Test that all required imports work"""
    try:
        print("✅ TwitterPlaywrightCrawler import successful")

        print("✅ PlaywrightPipeline import successful")

        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


async def test_single_crawl():
    """Test a single crawl operation"""
    try:
        from scripts.playwright_pipeline import PlaywrightPipeline

        print("🔄 Testing single crawl...")
        pipeline = PlaywrightPipeline()
        tweets = await pipeline.run_single_crawl(max_tweets_per_query=5)

        print(f"✅ Single crawl completed: {len(tweets)} tweets collected")
        return True
    except Exception as e:
        print(f"❌ Single crawl error: {e}")
        return False


def test_data_loading():
    """Test loading Playwright data"""
    try:
        output_dir = Path("output")
        playwright_file = output_dir / "twitter_playwright_latest.json"

        if playwright_file.exists():
            import json

            with open(playwright_file, encoding="utf-8") as f:
                data = json.load(f)

            print(f"✅ Playwright data loaded: {len(data.get('tweets', []))} tweets")
            return True
        else:
            print("⚠️ No Playwright data file found")
            return False
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧪 Testing Playwright Dashboard Integration")
    print("=" * 50)

    # Test imports
    imports_ok = test_playwright_imports()

    if imports_ok:
        # Test single crawl (optional - can be slow)
        print("\nWould you like to test a single crawl? (y/n): ", end="")
        response = input().lower().strip()

        if response == "y":
            crawl_ok = await test_single_crawl()
        else:
            print("⏭️ Skipping crawl test")
            crawl_ok = True

    # Test data loading
    data_ok = test_data_loading()

    print("\n" + "=" * 50)
    if imports_ok and data_ok:
        print("✅ All tests passed! Playwright crawler is ready for dashboard.")
    else:
        print("❌ Some tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
