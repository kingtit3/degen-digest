#!/usr/bin/env python3
"""
Test script to verify content cleaning functions
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import clean_post_content, clean_post_title


def test_content_cleaning():
    """Test the content cleaning functions"""

    print("Testing Content Cleaning Functions")
    print("=" * 50)

    # Test cases for content cleaning
    test_contents = [
        # JSON content
        '{"text": "Bitcoin reaches new all-time high!", "username": "crypto_analyst", "created_at": "2024-01-01"}',
        # Raw JSON with technical data
        '{"source": "twitter", "text": "Ethereum 2.0 upgrade successful", "engagement": {"likes": 100, "replies": 50}}',
        # Technical content
        'playwright_twitter_scraper source: twitter text: "DeFi yields are amazing right now!"',
        # Clean content
        "Bitcoin has reached a new milestone in adoption",
        # Empty content
        "",
        # Null content
        None,
    ]

    print("\nTesting clean_post_content():")
    for i, content in enumerate(test_contents, 1):
        cleaned = clean_post_content(content)
        print(f"Test {i}:")
        print(f"  Original: {content}")
        print(f"  Cleaned:  {cleaned}")
        print()

    # Test cases for title cleaning
    test_titles = [
        "No title",
        "playwright_twitter_scraper",
        "source: reddit",
        "Bitcoin Price Update",
        '{"title": "Ethereum News"}',
        "",
        None,
    ]

    print("\nTesting clean_post_title():")
    for i, title in enumerate(test_titles, 1):
        cleaned = clean_post_title(title)
        print(f"Test {i}:")
        print(f"  Original: {title}")
        print(f"  Cleaned:  {cleaned}")
        print()


if __name__ == "__main__":
    test_content_cleaning()
