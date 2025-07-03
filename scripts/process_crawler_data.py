#!/usr/bin/env python3
"""
Process Crawler Data for Digest Generation
Converts twitter_playwright_enhanced_*.json to twitter_raw.json format
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Google Cloud Storage imports
try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print(
        "Warning: Google Cloud Storage not available. Install with: pip install google-cloud-storage"
    )

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrawlerDataProcessor:
    def __init__(
        self,
        output_dir: str = "output",
        gcs_bucket: str = "degen-digest-data",
        project_id: str = "lucky-union-463615-t3",
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Google Cloud Storage configuration
        self.gcs_bucket_name = gcs_bucket
        self.project_id = project_id
        self.gcs_client = None
        self.gcs_bucket = None

        # Initialize Google Cloud Storage
        if GCS_AVAILABLE:
            try:
                self.gcs_client = storage.Client(project=project_id)
                self.gcs_bucket = self.gcs_client.bucket(gcs_bucket)
                logger.info(f"GCS initialized: {gcs_bucket} in project: {project_id}")
            except Exception as e:
                logger.error(f"Error accessing GCS bucket {gcs_bucket}: {e}")
                self.gcs_bucket = None
        else:
            logger.warning("Google Cloud Storage not available")

    def load_latest_crawler_data(self) -> list[dict[str, Any]]:
        """Load the latest crawler data from either GCS or local files"""
        tweets = []

        # Try to load from Google Cloud Storage first
        if self.gcs_bucket and GCS_AVAILABLE:
            try:
                # Try to get the latest file from GCS
                latest_cloud_path = "data/twitter_playwright_enhanced_latest.json"
                blob = self.gcs_bucket.blob(latest_cloud_path)

                if blob.exists():
                    logger.info("Loading latest crawler data from GCS...")
                    content = blob.download_as_text()
                    data = json.loads(content)
                    tweets = data.get("tweets", [])
                    logger.info(f"Loaded {len(tweets)} tweets from GCS")
                    return tweets
                else:
                    logger.warning("Latest crawler data not found in GCS")
            except Exception as e:
                logger.error(f"Error loading from GCS: {e}")

        # Fall back to local files
        logger.info("Loading latest crawler data from local files...")
        latest_file = self.output_dir / "twitter_playwright_enhanced_latest.json"

        if latest_file.exists():
            try:
                with open(latest_file, encoding="utf-8") as f:
                    data = json.load(f)
                tweets = data.get("tweets", [])
                logger.info(f"Loaded {len(tweets)} tweets from local file")
            except Exception as e:
                logger.error(f"Error loading local file: {e}")
        else:
            logger.warning("No local crawler data found")

        return tweets

    def convert_to_raw_format(
        self, tweets: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Convert crawler data to twitter_raw.json format"""
        raw_tweets = []

        for tweet in tweets:
            try:
                # Extract basic tweet data
                raw_tweet = {
                    "id": tweet.get("id", ""),
                    "text": tweet.get("text", ""),
                    "date": tweet.get("created_at", tweet.get("timestamp", "")),
                    "likeCount": tweet.get("like_count", tweet.get("likes", 0)),
                    "retweetCount": tweet.get(
                        "retweet_count", tweet.get("retweets", 0)
                    ),
                    "replyCount": tweet.get("reply_count", tweet.get("replies", 0)),
                    "quoteCount": tweet.get("quote_count", tweet.get("quotes", 0)),
                    "viewCount": tweet.get("view_count", tweet.get("views", 0)),
                    "user": {
                        "username": tweet.get("username", ""),
                        "screen_name": tweet.get("username", ""),
                        "followersCount": tweet.get("followers_count", 0),
                        "verified": tweet.get("verified", False),
                    },
                    "url": tweet.get("url", ""),
                    "source_type": tweet.get("source_type", "unknown"),
                    "sentiment": tweet.get("sentiment", {}),
                    "engagement_score": tweet.get("engagement_score", 0),
                    "collected_at": tweet.get(
                        "collected_at", datetime.now(timezone.utc).isoformat()
                    ),
                }

                raw_tweets.append(raw_tweet)

            except Exception as e:
                logger.error(f"Error converting tweet: {e}")
                continue

        logger.info(f"Converted {len(raw_tweets)} tweets to raw format")
        return raw_tweets

    def save_raw_data(self, raw_tweets: list[dict[str, Any]]):
        """Save data in twitter_raw.json format"""
        try:
            # Save locally
            raw_file = self.output_dir / "twitter_raw.json"
            with open(raw_file, "w", encoding="utf-8") as f:
                json.dump(raw_tweets, f, indent=2, default=str)

            logger.info(f"Saved {len(raw_tweets)} tweets to {raw_file}")

            # Upload to Google Cloud Storage
            if self.gcs_bucket and GCS_AVAILABLE:
                try:
                    cloud_path = "data/twitter_raw.json"
                    blob = self.gcs_bucket.blob(cloud_path)
                    blob.upload_from_filename(str(raw_file))
                    logger.info(f"Uploaded to GCS: {cloud_path}")
                except Exception as e:
                    logger.error(f"Error uploading to GCS: {e}")

        except Exception as e:
            logger.error(f"Error saving raw data: {e}")

    def process_and_save(self):
        """Main processing function"""
        logger.info("🚀 Starting crawler data processing...")

        # Load latest crawler data
        tweets = self.load_latest_crawler_data()

        if not tweets:
            logger.warning("No crawler data found to process")
            return False

        # Convert to raw format
        raw_tweets = self.convert_to_raw_format(tweets)

        if not raw_tweets:
            logger.warning("No tweets converted to raw format")
            return False

        # Save in twitter_raw.json format
        self.save_raw_data(raw_tweets)

        logger.info(
            f"✅ Successfully processed {len(raw_tweets)} tweets for digest generation"
        )
        return True


def main():
    """Main function"""
    processor = CrawlerDataProcessor()
    success = processor.process_and_save()

    if success:
        print("✅ Crawler data processed successfully!")
        print("📄 Data is now available as twitter_raw.json for digest generation")
    else:
        print("❌ Failed to process crawler data")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
