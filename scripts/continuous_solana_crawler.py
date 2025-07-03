#!/usr/bin/env python3
"""
Continuous Solana Twitter Crawler
Runs 18 hours a day with smart scheduling and anti-detection measures
"""

import asyncio
import json
import logging
import random
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/continuous_crawler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ContinuousSolanaCrawler:
    def __init__(
        self,
        username: str,
        password: str,
        cookies_path: str | None = None,
        user_agent: str | None = None,
        output_dir: str = "output",
        start_hour: int = 6,  # Start at 6 AM
        end_hour: int = 0,  # End at midnight (24 hours)
        crawl_interval_minutes: int = 30,
        max_retries: int = 3,
    ):
        self.username = username
        self.password = password
        self.cookies_path = cookies_path
        self.user_agent = user_agent
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Time settings (18 hours: 6 AM to 12 AM)
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
            "last_crawl_time": None,
            "start_time": None,
        }

        # Anti-detection settings
        self.variable_intervals = True
        self.random_delays = True

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.is_running = False

    def is_active_hours(self) -> bool:
        """Check if we're within active crawling hours"""
        now = datetime.now()
        current_hour = now.hour

        if self.end_hour == 0:  # Midnight
            return current_hour >= self.start_hour
        else:
            if self.start_hour <= self.end_hour:
                return self.start_hour <= current_hour < self.end_hour
            else:  # Crosses midnight
                return current_hour >= self.start_hour or current_hour < self.end_hour

    def get_next_crawl_delay(self) -> int:
        """Get delay until next crawl with anti-detection randomization"""
        if self.variable_intervals:
            # Randomize interval by ±20%
            base_interval = self.crawl_interval_minutes * 60
            variation = random.uniform(0.8, 1.2)
            return int(base_interval * variation)
        else:
            return self.crawl_interval_minutes * 60

    async def run_single_crawl_session(self) -> bool:
        """Run a single crawl session with retry logic"""
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"Starting crawl session (attempt {attempt + 1}/{self.max_retries})"
                )

                # Create crawler instance with GCS integration
                crawler = EnhancedTwitterPlaywrightCrawler(
                    headless=True,  # Run headless for continuous operation
                    output_dir=str(self.output_dir),
                    username=self.username,
                    password=self.password,
                    cookies_path=self.cookies_path,
                    user_agent=self.user_agent,
                    gcs_bucket="degen-digest-data",  # Save directly to GCS
                    project_id="lucky-union-463615-t3",
                )

                # Run the crawl
                tweets = await crawler.run_solana_focused_crawl(
                    max_for_you_tweets=random.randint(20, 40),
                    max_followed_accounts=random.randint(15, 25),
                    max_tweets_per_user=random.randint(8, 15),
                    max_saved_posts=random.randint(5, 10),
                )

                # Update statistics
                self.session_stats["total_crawls"] += 1
                self.session_stats["successful_crawls"] += 1
                self.session_stats["total_tweets_collected"] += len(tweets)
                self.session_stats["last_crawl_time"] = datetime.now(
                    timezone.utc
                ).isoformat()

                logger.info(f"Crawl session successful: {len(tweets)} tweets collected")
                return True

            except Exception as e:
                logger.error(f"Crawl session failed (attempt {attempt + 1}): {e}")
                self.session_stats["failed_crawls"] += 1

                if attempt < self.max_retries - 1:
                    # Wait before retry with exponential backoff
                    retry_delay = (2**attempt) * 60  # 2, 4, 8 minutes
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("All retry attempts failed")
                    return False

    async def save_session_stats(self):
        """Save current session statistics"""
        stats_file = self.output_dir / "crawler_stats.json"
        stats_data = {
            "session_stats": self.session_stats,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "crawler_config": {
                "start_hour": self.start_hour,
                "end_hour": self.end_hour,
                "crawl_interval_minutes": self.crawl_interval_minutes,
                "username": self.username,
            },
        }

        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats_data, f, indent=2, default=str)

    async def run_continuous_crawler(self):
        """Main continuous crawler loop"""
        logger.info("🚀 Starting Continuous Solana Crawler")
        logger.info(
            f"📅 Active hours: {self.start_hour}:00 - {self.end_hour}:00 (18 hours)"
        )
        logger.info(f"⏰ Crawl interval: {self.crawl_interval_minutes} minutes")

        self.is_running = True
        self.session_stats["start_time"] = datetime.now(timezone.utc).isoformat()

        while self.is_running:
            try:
                datetime.now()

                # Check if we're in active hours
                if not self.is_active_hours():
                    # Sleep until active hours
                    logger.info("😴 Outside active hours, sleeping...")
                    await asyncio.sleep(60)  # Check every minute
                    continue

                # Run crawl session
                success = await self.run_single_crawl_session()

                if success:
                    # Calculate next crawl delay
                    next_delay = self.get_next_crawl_delay()

                    # Add random delay for anti-detection
                    if self.random_delays:
                        random_delay = random.randint(
                            30, 180
                        )  # 30 seconds to 3 minutes
                        next_delay += random_delay

                    logger.info(f"⏳ Next crawl in {next_delay//60} minutes")

                    # Sleep until next crawl
                    await asyncio.sleep(next_delay)
                else:
                    # If crawl failed, wait longer before retry
                    logger.warning(
                        "🔄 Crawl failed, waiting 10 minutes before retry..."
                    )
                    await asyncio.sleep(600)

                # Save stats periodically
                await self.save_session_stats()

            except Exception as e:
                logger.error(f"Error in continuous crawler loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

        logger.info("🛑 Continuous crawler stopped")

    async def get_status(self) -> dict:
        """Get current crawler status"""
        return {
            "is_running": self.is_running,
            "is_active_hours": self.is_active_hours(),
            "session_stats": self.session_stats,
            "next_crawl_delay": self.get_next_crawl_delay()
            if self.is_running
            else None,
        }


async def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Continuous Solana Twitter Crawler")
    parser.add_argument("--username", required=True, help="Twitter username")
    parser.add_argument("--password", required=True, help="Twitter password")
    parser.add_argument("--cookies", help="Path to cookies file")
    parser.add_argument("--user-agent", help="Custom user agent")
    parser.add_argument("--start-hour", type=int, default=6, help="Start hour (0-23)")
    parser.add_argument("--end-hour", type=int, default=0, help="End hour (0-23)")
    parser.add_argument(
        "--interval", type=int, default=30, help="Crawl interval in minutes"
    )

    args = parser.parse_args()

    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Create crawler
    crawler = ContinuousSolanaCrawler(
        username=args.username,
        password=args.password,
        cookies_path=args.cookies,
        user_agent=args.user_agent,
        start_hour=args.start_hour,
        end_hour=args.end_hour,
        crawl_interval_minutes=args.interval,
    )

    # Run continuous crawler
    await crawler.run_continuous_crawler()


if __name__ == "__main__":
    asyncio.run(main())
