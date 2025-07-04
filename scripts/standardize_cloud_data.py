#!/usr/bin/env python3
"""
Standardize Cloud Data Structure
Organizes all data in Google Cloud Storage with consistent naming and structure.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    print(
        "❌ Google Cloud Storage not available. Install with: pip install google-cloud-storage"
    )
    sys.exit(1)

# Standardized Cloud Configuration
GCS_CONFIG = {
    "project_id": "lucky-union-463615-t3",
    "bucket_name": "degen-digest-data",
    "data_structure": {
        "twitter": {
            "raw": "twitter_data/",
            "consolidated": "consolidated/twitter_consolidated.json",
            "latest": "consolidated/twitter_latest.json",
        },
        "reddit": {
            "raw": "reddit_data/",
            "consolidated": "consolidated/reddit_consolidated.json",
        },
        "telegram": {
            "raw": "telegram_data/",
            "consolidated": "consolidated/telegram_consolidated.json",
        },
        "news": {
            "raw": "news_data/",
            "consolidated": "consolidated/news_consolidated.json",
        },
        "crypto": {
            "raw": "crypto_data/",
            "consolidated": "consolidated/crypto_consolidated.json",
        },
        "analytics": {
            "stats": "analytics/crawler_stats.json",
            "metrics": "analytics/engagement_metrics.json",
        },
        "digests": {
            "latest": "digests/latest_digest.md",
            "archive": "digests/archive/",
        },
    },
}


def get_gcs_client():
    """Get Google Cloud Storage client"""
    try:
        client = storage.Client(project=GCS_CONFIG["project_id"])
        bucket = client.bucket(GCS_CONFIG["bucket_name"])
        return client, bucket
    except Exception as e:
        print(f"❌ GCS connection failed: {e}")
        return None, None


def list_gcs_files(bucket, prefix=""):
    """List all files in GCS with given prefix"""
    try:
        blobs = bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]
    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return []


def download_and_consolidate_twitter_data(bucket):
    """Download and consolidate all Twitter data from GCS"""
    print("🔄 Consolidating Twitter data...")

    # List all Twitter data files
    twitter_files = list_gcs_files(bucket, "twitter_data/")
    print(f"📁 Found {len(twitter_files)} Twitter data files")

    all_tweets = []
    total_files = 0

    for file_path in twitter_files:
        if file_path.endswith(".json"):
            try:
                blob = bucket.blob(file_path)
                content = blob.download_as_text()
                data = json.loads(content)

                # Extract tweets from different possible structures
                if isinstance(data, dict):
                    if "tweets" in data:
                        tweets = data["tweets"]
                    elif "data" in data:
                        tweets = data["data"]
                    else:
                        tweets = [data]  # Single tweet
                elif isinstance(data, list):
                    tweets = data
                else:
                    continue

                # Add source file info to each tweet
                for tweet in tweets:
                    if isinstance(tweet, dict):
                        tweet["source_file"] = file_path
                        tweet["collected_at"] = datetime.now().isoformat()

                all_tweets.extend(tweets)
                total_files += 1

                print(f"  ✅ Processed {file_path} ({len(tweets)} tweets)")

            except Exception as e:
                print(f"  ❌ Error processing {file_path}: {e}")

    # Remove duplicates based on tweet ID or content
    unique_tweets = []
    seen_ids = set()
    seen_content = set()

    for tweet in all_tweets:
        if isinstance(tweet, dict):
            tweet_id = tweet.get("id") or tweet.get("tweet_id")
            content = tweet.get("text", "")[:100]  # First 100 chars for deduplication

            if tweet_id and tweet_id not in seen_ids:
                unique_tweets.append(tweet)
                seen_ids.add(tweet_id)
            elif content and content not in seen_content:
                unique_tweets.append(tweet)
                seen_content.add(content)

    print(
        f"📊 Consolidated {len(unique_tweets)} unique tweets from {total_files} files"
    )

    # Create consolidated structure
    consolidated_data = {
        "metadata": {
            "consolidated_at": datetime.now().isoformat(),
            "total_tweets": len(unique_tweets),
            "source_files": total_files,
            "unique_tweets": len(unique_tweets),
        },
        "tweets": unique_tweets,
    }

    return consolidated_data


def upload_consolidated_data(bucket, source_name, data):
    """Upload consolidated data to GCS"""
    try:
        consolidated_path = GCS_CONFIG["data_structure"][source_name]["consolidated"]
        blob = bucket.blob(consolidated_path)

        # Upload as JSON
        blob.upload_from_string(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type="application/json",
        )

        print(f"✅ Uploaded consolidated {source_name} data to {consolidated_path}")
        return True

    except Exception as e:
        print(f"❌ Error uploading {source_name} data: {e}")
        return False


def create_crawler_analytics(bucket):
    """Create crawler analytics from available data"""
    print("📈 Creating crawler analytics...")

    # Get Twitter data for analytics
    twitter_files = list_gcs_files(bucket, "twitter_data/")

    analytics = {
        "session_stats": {
            "total_crawls": len(twitter_files),
            "successful_crawls": len([f for f in twitter_files if f.endswith(".json")]),
            "total_tweets_collected": 0,
            "last_crawl_time": None,
            "first_crawl_time": None,
        },
        "source_stats": {
            "twitter": len(twitter_files),
            "reddit": len(list_gcs_files(bucket, "reddit_data/")),
            "telegram": len(list_gcs_files(bucket, "telegram_data/")),
            "news": len(list_gcs_files(bucket, "news_data/")),
            "crypto": len(list_gcs_files(bucket, "crypto_data/")),
        },
        "generated_at": datetime.now().isoformat(),
    }

    # Calculate tweet count from consolidated data
    try:
        consolidated_blob = bucket.blob(
            GCS_CONFIG["data_structure"]["twitter"]["consolidated"]
        )
        if consolidated_blob.exists():
            content = consolidated_blob.download_as_text()
            data = json.loads(content)
            analytics["session_stats"]["total_tweets_collected"] = len(
                data.get("tweets", [])
            )
    except Exception as e:
        print(f"⚠️ Could not get tweet count: {e}")

    return analytics


def create_engagement_metrics(bucket):
    """Create engagement metrics from available data"""
    print("📊 Creating engagement metrics...")

    try:
        # Get consolidated Twitter data
        consolidated_blob = bucket.blob(
            GCS_CONFIG["data_structure"]["twitter"]["consolidated"]
        )
        if not consolidated_blob.exists():
            return None

        content = consolidated_blob.download_as_text()
        data = json.loads(content)
        tweets = data.get("tweets", [])

        if not tweets:
            return None

        # Calculate engagement metrics
        total_likes = 0
        total_retweets = 0
        total_replies = 0
        engagement_scores = []

        for tweet in tweets:
            if isinstance(tweet, dict):
                likes = tweet.get("like_count", 0) or tweet.get("likes", 0)
                retweets = tweet.get("retweet_count", 0) or tweet.get("retweets", 0)
                replies = tweet.get("reply_count", 0) or tweet.get("replies", 0)

                total_likes += likes
                total_retweets += retweets
                total_replies += replies

                # Calculate engagement score
                engagement_score = min(100, (likes + retweets * 2 + replies * 3) / 10)
                engagement_scores.append(engagement_score)

        metrics = {
            "summary": {
                "total_tweets": len(tweets),
                "total_likes": total_likes,
                "total_retweets": total_retweets,
                "total_replies": total_replies,
                "avg_engagement_score": sum(engagement_scores) / len(engagement_scores)
                if engagement_scores
                else 0,
            },
            "engagement_distribution": {
                "high_engagement": len([s for s in engagement_scores if s > 50]),
                "medium_engagement": len(
                    [s for s in engagement_scores if 20 <= s <= 50]
                ),
                "low_engagement": len([s for s in engagement_scores if s < 20]),
            },
            "generated_at": datetime.now().isoformat(),
        }

        return metrics

    except Exception as e:
        print(f"❌ Error creating engagement metrics: {e}")
        return None


def main():
    """Main function to standardize cloud data"""
    print("🚀 Starting Cloud Data Standardization...")
    print("=" * 50)

    # Get GCS client
    client, bucket = get_gcs_client()
    if not bucket:
        print("❌ Failed to connect to Google Cloud Storage")
        return

    print(f"✅ Connected to GCS bucket: {GCS_CONFIG['bucket_name']}")

    # 1. Consolidate Twitter data
    twitter_consolidated = download_and_consolidate_twitter_data(bucket)
    if twitter_consolidated:
        upload_consolidated_data(bucket, "twitter", twitter_consolidated)

    # 2. Create analytics
    analytics = create_crawler_analytics(bucket)
    if analytics:
        try:
            analytics_blob = bucket.blob(
                GCS_CONFIG["data_structure"]["analytics"]["stats"]
            )
            analytics_blob.upload_from_string(
                json.dumps(analytics, indent=2), content_type="application/json"
            )
            print("✅ Uploaded crawler analytics")
        except Exception as e:
            print(f"❌ Error uploading analytics: {e}")

    # 3. Create engagement metrics
    metrics = create_engagement_metrics(bucket)
    if metrics:
        try:
            metrics_blob = bucket.blob(
                GCS_CONFIG["data_structure"]["analytics"]["metrics"]
            )
            metrics_blob.upload_from_string(
                json.dumps(metrics, indent=2), content_type="application/json"
            )
            print("✅ Uploaded engagement metrics")
        except Exception as e:
            print(f"❌ Error uploading metrics: {e}")

    # 4. Create placeholder files for other sources
    sources = ["reddit", "telegram", "news", "crypto"]
    for source in sources:
        try:
            consolidated_blob = bucket.blob(
                GCS_CONFIG["data_structure"][source]["consolidated"]
            )
            if not consolidated_blob.exists():
                placeholder_data = {
                    "metadata": {
                        "source": source,
                        "consolidated_at": datetime.now().isoformat(),
                        "status": "placeholder",
                    },
                    "data": [],
                }
                consolidated_blob.upload_from_string(
                    json.dumps(placeholder_data, indent=2),
                    content_type="application/json",
                )
                print(f"✅ Created placeholder for {source}")
        except Exception as e:
            print(f"❌ Error creating {source} placeholder: {e}")

    print("\n" + "=" * 50)
    print("✅ Cloud Data Standardization Complete!")
    print("\n📁 Standardized Structure:")
    for source, paths in GCS_CONFIG["data_structure"].items():
        print(f"  {source}:")
        for key, path in paths.items():
            print(f"    {key}: {path}")


if __name__ == "__main__":
    main()
