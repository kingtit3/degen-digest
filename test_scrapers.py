#!/usr/bin/env python3
"""
Test individual scrapers to see what's working
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))


def test_reddit():
    """Test Reddit scraper"""
    print("🔄 Testing Reddit scraper...")
    try:
        from scrapers.reddit_rss import scrape_reddit

        posts = scrape_reddit(["crypto", "bitcoin", "ethereum", "solana"])
        print(f"✅ Reddit: {len(posts)} posts found")
        return posts
    except Exception as e:
        print(f"❌ Reddit failed: {e}")
        return []


def test_news():
    """Test News scraper"""
    print("🔄 Testing News scraper...")
    try:
        from scrapers.newsapi_headlines import fetch_headlines

        articles = fetch_headlines()
        print(f"✅ News: {len(articles)} articles found")
        return articles
    except Exception as e:
        print(f"❌ News failed: {e}")
        return []


def test_crypto():
    """Test Crypto scraper"""
    print("🔄 Testing Crypto scraper...")
    try:
        from scrapers.coingecko_gainers import fetch_top_gainers

        gainers = fetch_top_gainers(10)
        print(f"✅ Crypto: {len(gainers)} gainers found")
        return gainers
    except Exception as e:
        print(f"❌ Crypto failed: {e}")
        return []


def main():
    """Test all scrapers"""
    print("🧪 Testing Individual Scrapers")
    print("=" * 40)

    results = {}

    # Test each scraper
    results["reddit"] = test_reddit()
    print()

    results["news"] = test_news()
    print()

    results["crypto"] = test_crypto()
    print()

    # Summary
    print("=" * 40)
    print("📊 SUMMARY")
    print("=" * 40)

    total_items = 0
    for source, items in results.items():
        count = len(items)
        total_items += count
        status = "✅" if count > 0 else "❌"
        print(f"{status} {source.title()}: {count} items")

    print(f"\n📈 Total: {total_items} items")

    # Save results
    output_file = Path("output/test_scrapers_results.json")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
