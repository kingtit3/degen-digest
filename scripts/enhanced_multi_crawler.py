#!/usr/bin/env python3
"""
Enhanced Multi-Source Crawler
Extends the existing Twitter crawler to include Reddit, News, and Crypto sources
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("Warning: Google Cloud Storage not available")

# Import the existing Twitter crawler
from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/enhanced_crawler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Load environment variables from .env at startup
load_dotenv()


class EnhancedMultiSourceCrawler:
    def __init__(
        self,
        username: str,
        password: str,
        cookies_path: str | None = None,
        user_agent: str | None = None,
        output_dir: str = "/tmp",
        start_hour: int = 6,
        end_hour: int = 0,
        crawl_interval_minutes: int = 30,
        max_retries: int = 3,
    ):
        # Twitter credentials
        self.username = username
        self.password = password
        self.cookies_path = cookies_path
        self.user_agent = user_agent
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Log loaded Twitter credentials (mask password)
        logger.info(f"Loaded Twitter username: {self.username}")
        logger.info(
            f"Loaded Twitter password: {'*' * len(self.password) if self.password else None}"
        )

        # Time settings
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.crawl_interval_minutes = crawl_interval_minutes
        self.max_retries = max_retries

        # Crawler state
        self.is_running = False
        self.current_session = None
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

        # Cloud configuration
        self.cloud_only = True
        self.gcs_bucket = "degen-digest-data"
        self.project_id = "lucky-union-463615-t3"

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

    async def crawl_reddit_simple(self) -> dict[str, Any]:
        """Simple Reddit RSS crawler"""
        try:
            logger.info("🔄 Starting Reddit crawl...")

            import requests

            # Reddit RSS feeds
            feeds = [
                "https://www.reddit.com/r/CryptoCurrency/new/.rss",
                "https://www.reddit.com/r/Solana/new/.rss",
                "https://www.reddit.com/r/Bitcoin/new/.rss",
                "https://www.reddit.com/r/Ethereum/new/.rss",
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

            self.session_stats["total_reddit_posts"] += len(all_posts)
            logger.info(f"✅ Reddit crawl completed: {len(all_posts)} posts")
            return data

        except Exception as e:
            logger.error(f"❌ Reddit crawl failed: {e}")
            return {
                "posts": [],
                "metadata": {"source": "reddit", "status": "error", "error": str(e)},
            }

    def crawl_news_simple(self) -> dict[str, Any]:
        """Simple News API crawler"""
        try:
            logger.info("🔄 Starting News crawl...")

            import requests

            # Check for API key
            api_key = os.getenv("NEWSAPI_KEY")
            if not api_key:
                logger.warning("⚠️ NEWSAPI_KEY not found, using fallback")
                # Return some basic crypto news from a public source
                articles = [
                    {
                        "title": "Crypto Market Update",
                        "summary": "Latest developments in cryptocurrency markets",
                        "link": "https://cointelegraph.com",
                        "published": datetime.now(UTC).isoformat(),
                    }
                ]
            else:
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
                    else:
                        logger.warning(f"News API returned HTTP {response.status_code}")
                        articles = []

                except Exception as e:
                    logger.warning(f"News API failed: {e}")
                    articles = []

            data = {
                "articles": articles,
                "metadata": {
                    "source": "news",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": len(articles),
                    "status": "success",
                },
            }

            self.session_stats["total_news_articles"] += len(articles)
            logger.info(f"✅ News crawl completed: {len(articles)} articles")
            return data

        except Exception as e:
            logger.error(f"❌ News crawl failed: {e}")
            return {
                "articles": [],
                "metadata": {"source": "news", "status": "error", "error": str(e)},
            }

    def crawl_crypto_simple(self) -> dict[str, Any]:
        """Simple CoinGecko API crawler"""
        try:
            logger.info("🔄 Starting Crypto crawl...")

            import requests

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
                    coins = response.json()
                    gainers = []

                    for coin in coins[:10]:  # Top 10 gainers
                        gainers.append(
                            {
                                "title": f"{coin['symbol'].upper()} +{coin.get('price_change_percentage_24h', 0):.1f}%",
                                "summary": f"{coin['name']} price: ${coin.get('current_price', 0):.4g}",
                                "link": f"https://www.coingecko.com/en/coins/{coin['id']}",
                                "published": datetime.now(UTC).isoformat(),
                                "price_change": coin.get(
                                    "price_change_percentage_24h", 0
                                ),
                            }
                        )
                else:
                    logger.warning(
                        f"CoinGecko API returned HTTP {response.status_code}"
                    )
                    gainers = []

            except Exception as e:
                logger.warning(f"CoinGecko API failed: {e}")
                gainers = []

            data = {
                "gainers": gainers,
                "metadata": {
                    "source": "crypto",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": len(gainers),
                    "status": "success",
                },
            }

            self.session_stats["total_crypto_gainers"] += len(gainers)
            logger.info(f"✅ Crypto crawl completed: {len(gainers)} gainers")
            return data

        except Exception as e:
            logger.error(f"❌ Crypto crawl failed: {e}")
            return {
                "gainers": [],
                "metadata": {"source": "crypto", "status": "error", "error": str(e)},
            }

    def crawl_reddit_full(self) -> dict[str, Any]:
        """Full Reddit RSS crawler using the proper scraper"""
        try:
            logger.info("🔄 Starting full Reddit crawl...")

            # Import and use the full Reddit scraper
            import json
            from pathlib import Path

            from scrapers.reddit_rss import scrape_reddit

            # Load keywords
            keywords_file = Path("config/keywords.json")
            if keywords_file.exists():
                keywords = json.loads(keywords_file.read_text())
                reddit_keywords = keywords.get("reddit", [])
            else:
                reddit_keywords = [
                    "crypto",
                    "bitcoin",
                    "ethereum",
                    "solana",
                    "defi",
                    "nft",
                ]

            # Use the full scraper - call it directly since it's not async
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

            self.session_stats["total_reddit_posts"] += len(posts)
            logger.info(f"✅ Full Reddit crawl completed: {len(posts)} posts")
            return data

        except Exception as e:
            logger.error(f"❌ Full Reddit crawl failed: {e}")
            return {
                "posts": [],
                "metadata": {"source": "reddit", "status": "error", "error": str(e)},
            }

    def crawl_news_full(self) -> dict[str, Any]:
        """Full News API crawler using the proper scraper"""
        try:
            logger.info("🔄 Starting full News crawl...")

            # Import and use the full News scraper
            from scrapers.newsapi_headlines import fetch_headlines

            # Use the full scraper
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

            self.session_stats["total_news_articles"] += len(articles)
            logger.info(f"✅ Full News crawl completed: {len(articles)} articles")
            return data

        except Exception as e:
            logger.error(f"❌ Full News crawl failed: {e}")
            return {
                "articles": [],
                "metadata": {"source": "news", "status": "error", "error": str(e)},
            }

    async def run_single_crawl_session(self):
        logger = self.logger
        logger.info("🔄 Starting enhanced crawl session...")
        # 1. Twitter crawl (direct execution, with timeout and granular logging)
        logger.info("🔄 [TWITTER] Starting Twitter crawl...")
        tweets = []
        twitter_status = "not_run"
        try:
            twitter_username = os.environ.get("TWITTER_USERNAME")
            twitter_password = os.environ.get("TWITTER_PASSWORD")
            cookies_path = os.environ.get("TWITTER_COOKIES_PATH")
            user_agent = os.environ.get("TWITTER_USER_AGENT")
            gcs_bucket = self.gcs_bucket
            project_id = self.project_id
            output_dir = str(self.output_dir)

            if not twitter_username or not twitter_password:
                logger.warning(
                    "⚠️ [TWITTER] Credentials not set, skipping Twitter crawl."
                )
            else:
                twitter_crawler = EnhancedTwitterPlaywrightCrawler(
                    headless=True,
                    output_dir=output_dir,
                    username=twitter_username,
                    password=twitter_password,
                    cookies_path=cookies_path,
                    user_agent=user_agent,
                    gcs_bucket=gcs_bucket,
                    project_id=project_id,
                )
                try:
                    logger.info("🔄 [TWITTER] Running Twitter crawl with timeout...")
                    tweets = await asyncio.wait_for(
                        twitter_crawler.run_solana_focused_crawl(
                            max_for_you_tweets=10,  # Reduced for debugging
                            max_followed_accounts=5,
                            max_tweets_per_user=3,
                            max_saved_posts=2,
                        ),
                        timeout=180,  # 3 minute timeout
                    )
                    twitter_status = "success"
                    logger.info(
                        f"✅ [TWITTER] Twitter crawl completed: {len(tweets)} tweets"
                    )
                except TimeoutError:
                    twitter_status = "timeout"
                    logger.error("❌ [TWITTER] Twitter crawl timed out after 3 minutes")
                except Exception as e:
                    twitter_status = "error"
                    logger.error(f"❌ [TWITTER] Twitter crawl failed: {e}")
        except Exception as e:
            twitter_status = "error"
            logger.error(f"❌ [TWITTER] Unexpected error in Twitter crawl setup: {e}")
        # Save Twitter results (even if empty)
        twitter_data = {
            "tweets": tweets,
            "metadata": {
                "source": "twitter",
                "crawled_at": datetime.now(UTC).isoformat(),
                "count": len(tweets),
                "status": twitter_status,
            },
        }
        self.upload_to_gcs(twitter_data, "twitter")

        # 2. Reddit crawl (sync) - Use full scraper
        reddit_data = self.crawl_reddit_full()
        self.upload_to_gcs(reddit_data, "reddit")

        # 3. News crawl (sync) - Use full scraper
        news_data = self.crawl_news_full()
        self.upload_to_gcs(news_data, "news")

        # 4. Crypto crawl (sync)
        crypto_data = self.crawl_crypto_simple()
        self.upload_to_gcs(crypto_data, "crypto")

        # 5. DEX Screener crawl (sync)
        try:
            from scrapers.dexscreener import main as dexscreener_main

            dexscreener_main()
            with open("output/dexscreener_raw.json") as f:
                dexscreener_data = json.load(f)
            self.upload_to_gcs(dexscreener_data, "dexscreener")
            logger.info(
                f"✅ DEX Screener crawl completed: {len(dexscreener_data.get('latest_token_profiles', []))} tokens"
            )
        except Exception as e:
            logger.error(f"❌ DEX Screener crawl failed: {e}")

        # 6. DexPaprika crawl (sync)
        try:
            from scrapers.dexpaprika import main as dexpaprika_main

            dexpaprika_main()
            with open("output/dexpaprika_raw.json") as f:
                dexpaprika_data = json.load(f)
            self.upload_to_gcs(dexpaprika_data, "dexpaprika")
            logger.info(
                f"✅ DexPaprika crawl completed: {len(dexpaprika_data.get('token_data', []))} tokens"
            )
        except Exception as e:
            logger.error(f"❌ DexPaprika crawl failed: {e}")

        # 7. Telegram crawl (sync)
        try:
            from scrapers.telegram_telethon import main as telegram_main

            telegram_main()
            with open("output/telegram_raw.json") as f:
                telegram_data = json.load(f)
            self.upload_to_gcs(telegram_data, "telegram")
            logger.info(
                f"✅ Telegram crawl completed: {len(telegram_data.get('messages', []))} messages"
            )
        except Exception as e:
            logger.error(f"❌ Telegram crawl failed: {e}")

        # Update statistics
        self.session_stats["total_crawls"] += 1
        self.session_stats["successful_crawls"] += 1
        self.session_stats["total_tweets_collected"] += len(tweets)
        self.session_stats["last_crawl_time"] = datetime.now(UTC).isoformat()

        logger.info("Enhanced crawl session successful:")
        logger.info(f"  - Twitter: {len(tweets)} tweets")
        logger.info(f"  - Reddit: {len(reddit_data.get('posts', []))} posts")
        logger.info(f"  - News: {len(news_data.get('articles', []))} articles")
        logger.info(f"  - Crypto: {len(crypto_data.get('gainers', []))} gainers")
        logger.info(f"  - Telegram: {len(telegram_data.get('messages', []))} messages")

        # Run data consolidation in background (non-blocking)
        logger.info("🔄 Starting data consolidation in background...")
        try:
            import subprocess

            # Start consolidation in background
            consolidation_process = subprocess.Popen(
                [sys.executable, "scripts/consolidate_cloud_data.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            logger.info("✅ Data consolidation started in background")
        except Exception as e:
            logger.error(f"❌ Error starting data consolidation: {e}")

        return True

    async def save_session_stats(self):
        """Save current session statistics to GCS"""
        try:
            # Create stats data
            stats_data = {
                "session_stats": self.session_stats,
                "last_updated": datetime.now(UTC).isoformat(),
                "crawler_config": {
                    "start_hour": self.start_hour,
                    "end_hour": self.end_hour,
                    "crawl_interval_minutes": self.crawl_interval_minutes,
                    "username": self.username,
                },
            }

            # Save to GCS
            client, bucket = self.get_gcs_client()
            if client and bucket:
                blob = bucket.blob("analytics/crawler_stats.json")
                blob.upload_from_string(
                    json.dumps(stats_data, indent=2, default=str),
                    content_type="application/json",
                )
                logger.info("📊 Session stats saved to GCS")

            # Also save locally
            stats_file = self.output_dir / "crawler_stats.json"
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(stats_data, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error saving session stats: {e}")

    async def get_status(self) -> dict:
        """Get current crawler status"""
        return {
            "status": "running" if self.is_running else "stopped",
            "session_stats": self.session_stats,
            "crawler_pid": os.getpid(),
            "crawler_running": self.is_running,
            "crawler_returncode": None,
        }

    async def run_continuous_crawler(self):
        """Main continuous crawler loop with all sources"""
        self.is_running = True
        self.session_stats["start_time"] = datetime.now(UTC).isoformat()

        logger.info("🚀 Starting Enhanced Multi-Source Crawler...")
        logger.info(f"📅 Active hours: {self.start_hour}:00 - {self.end_hour}:00")
        logger.info(f"⏰ Crawl interval: {self.crawl_interval_minutes} minutes")
        logger.info(f"☁️ Cloud-only mode: {self.cloud_only}")

        while self.is_running:
            try:
                # Check if we're in active hours
                now = datetime.now()
                current_hour = now.hour

                if self.end_hour == 0:  # Midnight
                    is_active = current_hour >= self.start_hour
                else:
                    if self.start_hour <= self.end_hour:
                        is_active = self.start_hour <= current_hour < self.end_hour
                    else:  # Crosses midnight
                        is_active = (
                            current_hour >= self.start_hour
                            or current_hour < self.end_hour
                        )

                if is_active:
                    logger.info(
                        f"🔄 Running enhanced crawl session at {now.strftime('%H:%M:%S')}"
                    )

                    success = await self.run_single_crawl_session()
                    if success:
                        await self.save_session_stats()

                    # Wait for next crawl
                    delay = self.crawl_interval_minutes * 60
                    logger.info(
                        f"⏳ Next crawl in {self.crawl_interval_minutes} minutes"
                    )
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
        logger.info("👋 Enhanced crawler stopped")


async def main():
    """Main function"""
    # Load credentials from environment
    username = os.getenv("TWITTER_USERNAME")
    password = os.getenv("TWITTER_PASSWORD")
    if not username or not password:
        logger.error("❌ Twitter credentials not found in environment")
        return
    else:
        logger.info(f"✅ Twitter credentials found: {username} / {'*' * len(password)}")

    # Create crawler
    crawler = EnhancedMultiSourceCrawler(
        username=username,
        password=password,
        output_dir="/tmp",
        start_hour=6,
        end_hour=0,
        crawl_interval_minutes=30,
    )

    # Run the crawler
    await crawler.run_continuous_crawler()


if __name__ == "__main__":
    asyncio.run(main())
