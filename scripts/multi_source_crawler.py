#!/usr/bin/env python3
"""
Multi-Source Crawler
Runs all data sources: Twitter, Reddit, News, Crypto, and Telegram
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("Warning: Google Cloud Storage not available")

from scrapers.coingecko_gainers import fetch_top_gainers
from scrapers.newsapi_headlines import fetch_headlines
from scrapers.reddit_rss import scrape_reddit

# Import scrapers
from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/multi_source_crawler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class MultiSourceCrawler:
    def __init__(
        self,
        twitter_username: str = None,
        twitter_password: str = None,
        output_dir: str = "/tmp",
        gcs_bucket: str = "degen-digest-data",
        project_id: str = "lucky-union-463615-t3",
    ):
        self.twitter_username = twitter_username
        self.twitter_password = twitter_password
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # GCS configuration
        self.gcs_bucket = gcs_bucket
        self.project_id = project_id
        self.gcs_available = GCS_AVAILABLE

        # Crawler stats
        self.stats = {
            "twitter": {"success": False, "count": 0, "error": None},
            "reddit": {"success": False, "count": 0, "error": None},
            "news": {"success": False, "count": 0, "error": None},
            "crypto": {"success": False, "count": 0, "error": None},
            "telegram": {"success": False, "count": 0, "error": None},
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def get_gcs_client(self):
        """Get GCS client if available"""
        if not self.gcs_available:
            return None, None

        try:
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.gcs_bucket)
            return client, bucket
        except Exception as e:
            logger.error(f"GCS connection failed: {e}")
            return None, None

    def upload_to_gcs(self, data: dict[str, Any], source: str):
        """Upload data to GCS"""
        client, bucket = self.get_gcs_client()
        if not bucket:
            return False

        try:
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{source}_data/{source}_{timestamp}.json"

            # Upload data
            blob = bucket.blob(filename)
            blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            # Also upload as latest
            latest_filename = f"{source}_data/{source}_latest.json"
            latest_blob = bucket.blob(latest_filename)
            latest_blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            logger.info(f"✅ Uploaded {source} data to GCS: {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload {source} data to GCS: {e}")
            return False

    async def crawl_twitter(self) -> dict[str, Any]:
        """Crawl Twitter data"""
        if not self.twitter_username or not self.twitter_password:
            logger.warning("⚠️ Twitter credentials not provided, skipping Twitter crawl")
            return {
                "tweets": [],
                "metadata": {"source": "twitter", "status": "skipped"},
            }

        try:
            logger.info("🔄 Starting Twitter crawl...")

            crawler = EnhancedTwitterPlaywrightCrawler(
                headless=True,
                output_dir=str(self.output_dir),
                username=self.twitter_username,
                password=self.twitter_password,
                gcs_bucket=self.gcs_bucket,
                project_id=self.project_id,
            )

            tweets = await crawler.run_solana_focused_crawl(
                max_for_you_tweets=30,
                max_followed_accounts=20,
                max_tweets_per_user=10,
                max_saved_posts=5,
            )

            data = {
                "tweets": tweets,
                "metadata": {
                    "source": "twitter",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": len(tweets),
                    "status": "success",
                },
            }

            self.stats["twitter"]["success"] = True
            self.stats["twitter"]["count"] = len(tweets)

            logger.info(f"✅ Twitter crawl completed: {len(tweets)} tweets")
            return data

        except Exception as e:
            logger.error(f"❌ Twitter crawl failed: {e}")
            self.stats["twitter"]["error"] = str(e)
            return {
                "tweets": [],
                "metadata": {"source": "twitter", "status": "error", "error": str(e)},
            }

    def crawl_reddit(self) -> dict[str, Any]:
        """Crawl Reddit data"""
        try:
            logger.info("🔄 Starting Reddit crawl...")

            # Load keywords
            keywords_path = Path("config/keywords.json")
            if keywords_path.exists():
                keywords = json.loads(keywords_path.read_text())
                reddit_keywords = keywords.get(
                    "reddit", ["crypto", "bitcoin", "ethereum", "solana"]
                )
            else:
                reddit_keywords = ["crypto", "bitcoin", "ethereum", "solana"]

            posts = scrape_reddit(reddit_keywords)

            data = {
                "posts": posts,
                "metadata": {
                    "source": "reddit",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": len(posts),
                    "status": "success",
                },
            }

            self.stats["reddit"]["success"] = True
            self.stats["reddit"]["count"] = len(posts)

            logger.info(f"✅ Reddit crawl completed: {len(posts)} posts")
            return data

        except Exception as e:
            logger.error(f"❌ Reddit crawl failed: {e}")
            self.stats["reddit"]["error"] = str(e)
            return {
                "posts": [],
                "metadata": {"source": "reddit", "status": "error", "error": str(e)},
            }

    def crawl_news(self) -> dict[str, Any]:
        """Crawl news data"""
        try:
            logger.info("🔄 Starting News crawl...")

            articles = fetch_headlines()

            data = {
                "articles": articles,
                "metadata": {
                    "source": "news",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": len(articles),
                    "status": "success",
                },
            }

            self.stats["news"]["success"] = True
            self.stats["news"]["count"] = len(articles)

            logger.info(f"✅ News crawl completed: {len(articles)} articles")
            return data

        except Exception as e:
            logger.error(f"❌ News crawl failed: {e}")
            self.stats["news"]["error"] = str(e)
            return {
                "articles": [],
                "metadata": {"source": "news", "status": "error", "error": str(e)},
            }

    def crawl_crypto(self) -> dict[str, Any]:
        """Crawl crypto data"""
        try:
            logger.info("🔄 Starting Crypto crawl...")

            gainers = fetch_top_gainers(20)

            data = {
                "gainers": gainers,
                "metadata": {
                    "source": "crypto",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": len(gainers),
                    "status": "success",
                },
            }

            self.stats["crypto"]["success"] = True
            self.stats["crypto"]["count"] = len(gainers)

            logger.info(f"✅ Crypto crawl completed: {len(gainers)} gainers")
            return data

        except Exception as e:
            logger.error(f"❌ Crypto crawl failed: {e}")
            self.stats["crypto"]["error"] = str(e)
            return {
                "gainers": [],
                "metadata": {"source": "crypto", "status": "error", "error": str(e)},
            }

    def crawl_telegram(self) -> dict[str, Any]:
        """Crawl Telegram data (placeholder for now)"""
        try:
            logger.info("🔄 Starting Telegram crawl...")

            # For now, return empty data since Telegram requires more setup
            data = {
                "messages": [],
                "metadata": {
                    "source": "telegram",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": 0,
                    "status": "not_implemented",
                },
            }

            self.stats["telegram"]["success"] = True
            self.stats["telegram"]["count"] = 0

            logger.info("✅ Telegram crawl completed (not implemented)")
            return data

        except Exception as e:
            logger.error(f"❌ Telegram crawl failed: {e}")
            self.stats["telegram"]["error"] = str(e)
            return {
                "messages": [],
                "metadata": {"source": "telegram", "status": "error", "error": str(e)},
            }

    async def run_all_crawlers(self):
        """Run all crawlers and upload data"""
        logger.info("🚀 Starting multi-source crawl...")

        # Run all crawlers
        results = {}

        # Twitter (async)
        results["twitter"] = await self.crawl_twitter()

        # Reddit (sync)
        results["reddit"] = self.crawl_reddit()

        # News (sync)
        results["news"] = self.crawl_news()

        # Crypto (sync)
        results["crypto"] = self.crawl_crypto()

        # Telegram (sync)
        results["telegram"] = self.crawl_telegram()

        # Upload all results to GCS
        for source, data in results.items():
            self.upload_to_gcs(data, source)

        # Save overall stats
        self.save_stats()

        # Print summary
        self.print_summary()

        return results

    def save_stats(self):
        """Save crawler statistics"""
        try:
            # Save to GCS
            client, bucket = self.get_gcs_client()
            if bucket:
                blob = bucket.blob("analytics/crawler_stats.json")
                blob.upload_from_string(
                    json.dumps(self.stats, indent=2), content_type="application/json"
                )
                logger.info("📊 Stats saved to GCS")

            # Also save locally
            stats_file = self.output_dir / "crawler_stats.json"
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving stats: {e}")

    def print_summary(self):
        """Print crawl summary"""
        print("\n" + "=" * 50)
        print("📊 MULTI-SOURCE CRAWL SUMMARY")
        print("=" * 50)

        total_items = 0
        successful_sources = 0

        for source, stats in self.stats.items():
            if source == "timestamp":
                continue

            status = "✅" if stats["success"] else "❌"
            count = stats["count"]
            error = stats.get("error", "")

            print(f"{status} {source.title()}: {count} items")
            if error:
                print(f"   Error: {error}")

            if stats["success"]:
                successful_sources += 1
                total_items += count

        print(f"\n📈 Total: {total_items} items from {successful_sources}/5 sources")
        print(f"⏰ Timestamp: {self.stats['timestamp']}")
        print("=" * 50)


async def main():
    """Main function"""
    # Get Twitter credentials from environment
    twitter_username = os.getenv("TWITTER_USERNAME")
    twitter_password = os.getenv("TWITTER_PASSWORD")

    # Create crawler
    crawler = MultiSourceCrawler(
        twitter_username=twitter_username,
        twitter_password=twitter_password,
        output_dir="/tmp",
        gcs_bucket="degen-digest-data",
        project_id="lucky-union-463615-t3",
    )

    # Run all crawlers
    await crawler.run_all_crawlers()


if __name__ == "__main__":
    asyncio.run(main())
