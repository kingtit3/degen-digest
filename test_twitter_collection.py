#!/usr/bin/env python3
"""
Test script to check Twitter data collection
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))


def test_environment():
    """Test if required environment variables are set"""
    print("🔍 Testing environment variables...")

    apify_token = os.getenv("APIFY_API_TOKEN")
    if apify_token:
        print(f"✅ APIFY_API_TOKEN found (length: {len(apify_token)})")
    else:
        print("❌ APIFY_API_TOKEN not found")
        return False

    return True


def test_config_files():
    """Test if configuration files exist"""
    print("\n🔍 Testing configuration files...")

    config_files = ["config/influencers.json", "config/keywords.json"]

    for file_path in config_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False

    return True


def test_twitter_scraper():
    """Test Twitter scraper directly"""
    print("\n🔍 Testing Twitter scraper...")

    try:
        import json

        from scrapers.twitter_apify import run_tweet_scraper

        # Load config
        with open("config/influencers.json") as f:
            influencers = json.load(f)

        with open("config/keywords.json") as f:
            keywords = json.load(f)

        print(f"📊 Found {len(influencers)} influencers")
        print(f"🔍 Found {len(keywords['twitter_search'])} search terms")

        # Test with a small subset
        test_accounts = influencers[:3]  # Just 3 accounts
        test_terms = keywords["twitter_search"][:2]  # Just 2 terms

        print(
            f"🧪 Testing with {len(test_accounts)} accounts and {len(test_terms)} terms..."
        )

        tweets = run_tweet_scraper(
            accounts=test_accounts,
            search_terms=test_terms,
            max_tweets=10,  # Small number for testing
            min_likes=10,
            min_retweets=5,
        )

        print(f"✅ Collected {len(tweets)} tweets")
        return len(tweets) > 0

    except Exception as e:
        print(f"❌ Twitter scraper failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_database():
    """Test database connection and content"""
    print("\n🔍 Testing database...")

    try:
        from storage.db import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check tweets table
        cursor.execute("SELECT COUNT(*) FROM tweets")
        tweet_count = cursor.fetchone()[0]
        print(f"📊 Database has {tweet_count} tweets")

        # Check recent tweets
        cursor.execute(
            "SELECT COUNT(*) FROM tweets WHERE created_at > datetime('now', '-1 day')"
        )
        recent_tweets = cursor.fetchone()[0]
        print(f"📊 Database has {recent_tweets} tweets from last 24 hours")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Testing Twitter data collection...\n")

    tests = [
        ("Environment Variables", test_environment),
        ("Configuration Files", test_config_files),
        ("Database", test_database),
        ("Twitter Scraper", test_twitter_scraper),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("📋 TEST RESULTS:")
    print("=" * 50)

    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if not result:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Twitter collection should work.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")

    return all_passed


if __name__ == "__main__":
    main()
