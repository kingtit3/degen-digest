#!/usr/bin/env python3
"""
Test version of enhanced crawler without Twitter authentication
"""

import asyncio
import json
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class TestEnhancedCrawler:
    def __init__(self):
        self.output_dir = Path("/tmp")
        self.output_dir.mkdir(exist_ok=True)

        # Cloud configuration
        self.gcs_bucket = "degen-digest-data"
        self.project_id = "lucky-union-463615-t3"

        # Crawler state
        self.is_running = False
        self.session_stats = {
            "total_crawls": 0,
            "successful_crawls": 0,
            "failed_crawls": 0,
            "total_tweets_collected": 0,
            "total_reddit_posts": 0,
            "total_news_articles": 0,
            "total_crypto_gainers": 0,
            "last_crawl_time": None,
            "start_time": None,
        }

    def get_gcs_client(self):
        """Get GCS client if available"""
        try:
            from google.cloud import storage

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

    def crawl_reddit_simple(self) -> dict[str, Any]:
        """Simple Reddit RSS crawler"""
        try:
            logger.info("🔄 Starting Reddit crawl...")

            import requests

            # Reddit RSS feeds
            feeds = [
                "https://www.reddit.com/r/CryptoCurrency/new/.rss",
                "https://www.reddit.com/r/Solana/new/.rss",
            ]

            all_posts = []

            for feed_url in feeds:
                try:
                    response = requests.get(feed_url, timeout=10)
                    if response.status_code == 200:
                        # Simple parsing - extract basic info
                        content = response.text

                        # Extract posts using simple parsing
                        import re

                        titles = re.findall(r"<title>(.*?)</title>", content)
                        links = re.findall(r"<link>(.*?)</link>", content)

                        # Filter out non-post entries
                        posts = []
                        for i, title in enumerate(titles):
                            if i < len(links) and "reddit.com/r/" in links[i]:
                                posts.append(
                                    {
                                        "title": title,
                                        "link": links[i],
                                        "subreddit": feed_url.split("/r/")[1].split(
                                            "/"
                                        )[0],
                                        "published": datetime.now(UTC).isoformat(),
                                    }
                                )

                        all_posts.extend(posts[:5])  # Limit to 5 posts per subreddit
                        logger.info(f"  ✅ {feed_url}: {len(posts)} posts")

                except Exception as e:
                    logger.warning(f"  ⚠️ Failed to fetch {feed_url}: {e}")

            data = {
                "posts": all_posts,
                "metadata": {
                    "source": "reddit",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": len(all_posts),
                    "status": "success",
                },
            }

            logger.info(f"✅ Reddit crawl completed: {len(all_posts)} posts")
            return data

        except Exception as e:
            logger.error(f"❌ Reddit crawl failed: {e}")
            return {
                "posts": [],
                "metadata": {
                    "source": "reddit",
                    "status": "error",
                    "error": str(e),
                },
            }

    def crawl_news_simple(self) -> dict[str, Any]:
        """Simple News API crawler"""
        try:
            logger.info("🔄 Starting News crawl...")

            import requests

            # News API configuration
            api_key = os.getenv("NEWSAPI_KEY")
            if not api_key:
                logger.warning("⚠️ NEWSAPI_KEY not set, skipping news crawl")
                return {
                    "articles": [],
                    "metadata": {
                        "source": "news",
                        "status": "error",
                        "error": "NEWSAPI_KEY not set",
                    },
                }

            # Keywords for crypto news
            keywords = ["bitcoin", "ethereum", "solana"]

            all_articles = []

            for keyword in keywords:
                try:
                    url = "https://newsapi.org/v2/everything"
                    params = {
                        "q": keyword,
                        "apiKey": api_key,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": 10,
                    }

                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        articles = data.get("articles", [])

                        for article in articles:
                            all_articles.append(
                                {
                                    "title": article.get("title", ""),
                                    "description": article.get("description", ""),
                                    "url": article.get("url", ""),
                                    "publishedAt": article.get("publishedAt", ""),
                                    "source": article.get("source", {}).get("name", ""),
                                    "keyword": keyword,
                                }
                            )

                        logger.info(f"  ✅ {keyword}: {len(articles)} articles")

                except Exception as e:
                    logger.warning(f"  ⚠️ Failed to fetch news for {keyword}: {e}")

            data = {
                "articles": all_articles,
                "metadata": {
                    "source": "news",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": len(all_articles),
                    "status": "success",
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
                    "status": "error",
                    "error": str(e),
                },
            }

    def crawl_crypto_simple(self) -> dict[str, Any]:
        """Simple CoinGecko crawler"""
        try:
            logger.info("🔄 Starting Crypto crawl...")

            import requests

            # CoinGecko API
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 10,
                "page": 1,
                "sparkline": False,
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()

                gainers = []
                for coin in data:
                    gainers.append(
                        {
                            "title": f"{coin['symbol'].upper()} {coin['price_change_percentage_24h']:+.2f}%",
                            "name": coin["name"],
                            "symbol": coin["symbol"].upper(),
                            "price": coin["current_price"],
                            "change_24h": coin["price_change_percentage_24h"],
                            "market_cap": coin["market_cap"],
                        }
                    )

                result = {
                    "gainers": gainers,
                    "metadata": {
                        "source": "crypto",
                        "crawled_at": datetime.now(UTC).isoformat(),
                        "count": len(gainers),
                        "status": "success",
                    },
                }

                logger.info(f"✅ Crypto crawl completed: {len(gainers)} gainers")
                return result

            else:
                logger.error(f"❌ CoinGecko API returned {response.status_code}")
                return {
                    "gainers": [],
                    "metadata": {
                        "source": "crypto",
                        "status": "error",
                        "error": f"API returned {response.status_code}",
                    },
                }

        except Exception as e:
            logger.error(f"❌ Crypto crawl failed: {e}")
            return {
                "gainers": [],
                "metadata": {
                    "source": "crypto",
                    "status": "error",
                    "error": str(e),
                },
            }

    async def run_single_crawl_session(self) -> bool:
        """Run a single crawl session without Twitter"""
        try:
            logger.info("Starting test crawl session (no Twitter)...")

            # 1. Reddit crawl
            reddit_data = self.crawl_reddit_simple()
            self.upload_to_gcs(reddit_data, "reddit")

            # 2. News crawl
            news_data = self.crawl_news_simple()
            self.upload_to_gcs(news_data, "news")

            # 3. Crypto crawl
            crypto_data = self.crawl_crypto_simple()
            self.upload_to_gcs(crypto_data, "crypto")

            # Update statistics
            self.session_stats["total_crawls"] += 1
            self.session_stats["successful_crawls"] += 1
            self.session_stats["total_reddit_posts"] += len(
                reddit_data.get("posts", [])
            )
            self.session_stats["total_news_articles"] += len(
                news_data.get("articles", [])
            )
            self.session_stats["total_crypto_gainers"] += len(
                crypto_data.get("gainers", [])
            )
            self.session_stats["last_crawl_time"] = datetime.now(UTC).isoformat()

            logger.info("Test crawl session successful:")
            logger.info(f"  - Reddit: {len(reddit_data.get('posts', []))} posts")
            logger.info(f"  - News: {len(news_data.get('articles', []))} articles")
            logger.info(f"  - Crypto: {len(crypto_data.get('gainers', []))} gainers")

            return True

        except Exception as e:
            logger.error(f"Test crawl session failed: {e}")
            self.session_stats["failed_crawls"] += 1
            return False

    async def run_continuous_crawler(self):
        """Main continuous crawler loop without Twitter"""
        self.is_running = True
        self.session_stats["start_time"] = datetime.now(UTC).isoformat()

        logger.info("🚀 Starting Test Enhanced Multi-Source Crawler (No Twitter)...")
        logger.info("📅 Active hours: 6:00 - 0:00")
        logger.info("⏰ Crawl interval: 30 minutes")
        logger.info("☁️ Cloud-only mode: true")

        while self.is_running:
            try:
                # Check if we're in active hours
                now = datetime.now()
                current_hour = now.hour

                # Active hours: 6 AM to 12 AM
                is_active = current_hour >= 6

                if is_active:
                    logger.info(
                        f"🔄 Running test crawl session at {now.strftime('%H:%M:%S')}"
                    )

                    success = await self.run_single_crawl_session()
                    if success:
                        logger.info("✅ Crawl session completed successfully")

                    # Wait for next crawl
                    delay = 30 * 60  # 30 minutes
                    logger.info("⏳ Next crawl in 30 minutes")
                    await asyncio.sleep(delay)
                else:
                    logger.info(
                        f"😴 Outside active hours ({current_hour}:00), sleeping..."
                    )
                    await asyncio.sleep(300)  # Sleep for 5 minutes

            except KeyboardInterrupt:
                logger.info("🛑 Received interrupt signal, shutting down...")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in main loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying

        self.is_running = False
        logger.info("👋 Test crawler stopped")


async def main():
    """Main function"""
    # Create crawler without Twitter credentials
    crawler = TestEnhancedCrawler()

    # Run the crawler
    await crawler.run_continuous_crawler()


if __name__ == "__main__":
    asyncio.run(main())
