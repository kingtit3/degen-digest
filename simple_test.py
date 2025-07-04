#!/usr/bin/env python3
"""
Simple test script
"""

import json
from pathlib import Path

import requests


def test_reddit_simple():
    """Test Reddit RSS feeds directly"""
    print("🔄 Testing Reddit RSS...")

    feeds = [
        "https://www.reddit.com/r/CryptoCurrency/new/.rss",
        "https://www.reddit.com/r/Solana/new/.rss",
    ]

    all_posts = []

    for feed_url in feeds:
        try:
            response = requests.get(feed_url, timeout=10)
            if response.status_code == 200:
                # Simple parsing - just count entries
                content = response.text
                entries = content.count("<entry>")
                print(f"✅ {feed_url}: {entries} entries")
                all_posts.extend([{"source": feed_url, "count": entries}])
            else:
                print(f"❌ {feed_url}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {feed_url}: {e}")

    return all_posts


def test_news_simple():
    """Test News API directly"""
    print("🔄 Testing News API...")

    # Check if API key is available
    import os

    api_key = os.getenv("NEWSAPI_KEY")

    if not api_key:
        print("⚠️ NEWSAPI_KEY not found in environment")
        return []

    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "crypto OR bitcoin OR ethereum OR solana",
            "language": "en",
            "pageSize": 10,
            "sortBy": "publishedAt",
            "apiKey": api_key,
        }

        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            print(f"✅ News API: {len(articles)} articles")
            return articles
        else:
            print(f"❌ News API: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ News API: {e}")
        return []


def test_crypto_simple():
    """Test CoinGecko API directly"""
    print("🔄 Testing CoinGecko API...")

    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "price_change_percentage_24h_desc",
            "per_page": 10,
            "page": 1,
        }

        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ CoinGecko: {len(data)} coins")
            return data
        else:
            print(f"❌ CoinGecko: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ CoinGecko: {e}")
        return []


def main():
    """Run simple tests"""
    print("🧪 Simple Scraper Tests")
    print("=" * 40)

    results = {}

    results["reddit"] = test_reddit_simple()
    print()

    results["news"] = test_news_simple()
    print()

    results["crypto"] = test_crypto_simple()
    print()

    # Summary
    print("=" * 40)
    print("📊 SUMMARY")
    print("=" * 40)

    for source, data in results.items():
        if isinstance(data, list) and data:
            print(f"✅ {source.title()}: {len(data)} items")
        else:
            print(f"❌ {source.title()}: No data")

    # Save results
    output_file = Path("output/simple_test_results.json")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
