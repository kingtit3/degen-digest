#!/usr/bin/env python3
"""
Simple test script to debug Reddit crawler
"""
import time

import requests


def test_reddit_rss():
    """Test Reddit RSS feeds directly"""
    feeds = [
        {
            "name": "CryptoMoonShots",
            "url": "https://www.reddit.com/r/CryptoMoonShots/new/.rss",
            "category": "memecoin",
        },
        {
            "name": "CryptoCurrency",
            "url": "https://www.reddit.com/r/CryptoCurrency/new/.rss",
            "category": "general",
        },
    ]

    for i, feed in enumerate(feeds):
        try:
            print(f"Testing {feed['name']}...")

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            response = requests.get(feed["url"], timeout=15, headers=headers)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                content = response.text
                print(f"Content length: {len(content)}")
                print(f"First 500 chars: {content[:500]}")
            else:
                print(f"Error: {response.text[:200]}")

            if i < len(feeds) - 1:
                time.sleep(2)

        except Exception as e:
            print(f"Exception: {e}")


if __name__ == "__main__":
    test_reddit_rss()
