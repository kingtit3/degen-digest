#!/usr/bin/env python3
"""
Simple test script to debug News crawler
"""
import os
import time

import requests


def test_news_api():
    """Test NewsAPI directly"""
    newsapi_key = "ffc45af6fcd94c4991eaefdc469346e8"

    queries = ["cryptocurrency bitcoin ethereum", "defi yield farming"]

    for i, query in enumerate(queries):
        try:
            print(f"Testing query: {query}...")

            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": newsapi_key,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 5,
                "page": 1,
            }

            response = requests.get(url, params=params, timeout=15)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                print(f"Found {len(articles)} articles")

                for j, article in enumerate(articles[:2]):
                    print(f"  Article {j+1}: {article.get('title', 'No title')}")

            else:
                print(f"Error: {response.text[:200]}")

            if i < len(queries) - 1:
                time.sleep(3)

        except Exception as e:
            print(f"Exception: {e}")


if __name__ == "__main__":
    test_news_api()
