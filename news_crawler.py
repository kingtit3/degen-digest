#!/usr/bin/env python3
"""
Standalone News Crawler Service
Deployed as a separate Cloud Run service for better isolation
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.append(str(Path(__file__).parent))

try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("Warning: Google Cloud Storage not available")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class NewsCrawler:
    def __init__(self):
        self.cloud_only = True
        self.gcs_bucket = "degen-digest-data"
        self.project_id = "lucky-union-463615-t3"
        self.newsapi_key = os.environ.get("NEWSAPI_KEY")

    def get_gcs_client(self):
        """Get GCS client if available"""
        if not GCS_AVAILABLE:
            return None, None

        try:
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(self.gcs_bucket)
            return client, bucket
        except Exception as e:
            logger.error(f"GCS connection failed: {e}")
            return None, None

    def upload_to_gcs(self, data: dict[str, Any]):
        """Upload data to GCS"""
        client, bucket = self.get_gcs_client()
        if not bucket:
            return False

        try:
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_data/news_{timestamp}.json"

            # Upload data
            blob = bucket.blob(filename)
            blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            # Also upload as latest
            latest_filename = "news_data/news_latest.json"
            latest_blob = bucket.blob(latest_filename)
            latest_blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            logger.info(f"✅ Uploaded news data to GCS: {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload news data to GCS: {e}")
            return False

    async def crawl_news(self) -> dict[str, Any]:
        """Crawl news from News API"""
        try:
            logger.info("🔄 Starting News crawl...")

            if not self.newsapi_key:
                logger.warning("⚠️ NEWSAPI_KEY not set, skipping news crawl")
                return {
                    "articles": [],
                    "metadata": {
                        "source": "news",
                        "crawled_at": datetime.now(UTC).isoformat(),
                        "count": 0,
                        "status": "skipped",
                        "error": "NEWSAPI_KEY not set",
                    },
                }

            import requests

            # News API keywords for crypto
            keywords = [
                "cryptocurrency",
                "bitcoin",
                "ethereum",
                "solana",
                "crypto",
                "blockchain",
                "defi",
                "nft",
                "web3",
                "metaverse",
                "binance",
                "coinbase",
                "trading",
                "altcoin",
                "meme coin",
            ]

            all_articles = []

            for keyword in keywords[:5]:  # Limit to 5 keywords to avoid rate limits
                try:
                    logger.info(f"  🔄 Fetching news for keyword: {keyword}")

                    url = "https://newsapi.org/v2/everything"
                    params = {
                        "q": keyword,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": 10,
                        "apiKey": self.newsapi_key,
                    }

                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        articles = []

                        if "articles" in data:
                            for article in data["articles"][
                                :5
                            ]:  # Top 5 articles per keyword
                                articles.append(
                                    {
                                        "title": article.get("title", ""),
                                        "description": article.get("description", ""),
                                        "url": article.get("url", ""),
                                        "source": article.get("source", {}).get(
                                            "name", ""
                                        ),
                                        "published_at": article.get("publishedAt", ""),
                                        "keyword": keyword,
                                        "content": article.get("content", ""),
                                    }
                                )

                        all_articles.extend(articles)
                        logger.info(f"  ✅ {keyword}: {len(articles)} articles")

                        # Small delay to avoid rate limits
                        await asyncio.sleep(1)

                    else:
                        logger.warning(
                            f"  ⚠️ News API returned {response.status_code} for {keyword}"
                        )

                except Exception as e:
                    logger.warning(f"  ⚠️ Failed to fetch news for {keyword}: {e}")

            data = {
                "articles": all_articles,
                "metadata": {
                    "source": "news",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": len(all_articles),
                    "status": "success",
                    "keywords_used": keywords[:5],
                },
            }

            logger.info(f"✅ News crawl completed: {len(all_articles)} articles")
            return data

        except Exception as e:
            logger.error(f"❌ News crawl failed: {e}")
            return {
                "articles": [],
                "metadata": {
                    "source": "news",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": 0,
                    "status": "error",
                    "error": str(e),
                },
            }

    async def run_single_crawl(self):
        """Run a single News crawl session"""
        logger.info("🔄 Running News crawl session...")

        # Crawl News
        news_data = await self.crawl_news()

        # Upload to GCS
        if self.upload_to_gcs(news_data):
            logger.info("✅ News crawl session completed successfully")
        else:
            logger.error("❌ Failed to upload News data")

        return news_data


async def main():
    """Main function for standalone News crawler"""
    crawler = NewsCrawler()

    # Run single crawl
    result = await crawler.run_single_crawl()

    logger.info("📊 Crawl Summary:")
    logger.info(f"  - News: {len(result['articles'])} articles")

    return result


if __name__ == "__main__":
    asyncio.run(main())
