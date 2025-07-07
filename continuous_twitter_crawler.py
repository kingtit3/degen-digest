#!/usr/bin/env python3
"""
Continuous Twitter Crawler - Runs 20 hours a day
Crawls: Following, For You, Explore, and Search pages
"""
import asyncio
import json
import logging
import os
import random
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Add current directory to path
sys.path.append(".")

from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("output/continuous_crawler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ContinuousTwitterCrawler:
    def __init__(self):
        self.crawler = None
        self.running = False
        self.crawl_sources = [
            {
                "name": "Following",
                "url": "https://twitter.com/home",
                "query": "following",
                "tweets_per_source": 50,
            },
            {
                "name": "For You",
                "url": "https://twitter.com/home",
                "query": "for_you",
                "tweets_per_source": 50,
            },
            {
                "name": "Explore",
                "url": "https://twitter.com/explore",
                "query": "explore",
                "tweets_per_source": 50,
            },
            {
                "name": "Crypto Search",
                "url": "https://twitter.com/search?q=crypto&src=typed_query&f=live",
                "query": "crypto",
                "tweets_per_source": 50,
            },
            {
                "name": "Bitcoin Search",
                "url": "https://twitter.com/search?q=bitcoin&src=typed_query&f=live",
                "query": "bitcoin",
                "tweets_per_source": 50,
            },
            {
                "name": "Solana Search",
                "url": "https://twitter.com/search?q=solana&src=typed_query&f=live",
                "query": "solana",
                "tweets_per_source": 50,
            },
        ]

        # Set credentials
        os.environ["TWITTER_USERNAME"] = "gorebroai"
        os.environ["TWITTER_PASSWORD"] = "firefireomg4321"

    async def setup_crawler(self):
        """Initialize the Twitter crawler"""
        try:
            self.crawler = EnhancedTwitterPlaywrightCrawler(
                headless=True,
                output_dir="output",
                cookies_path="output/twitter_cookies.json",
            )
            await self.crawler.setup_browser()
            logger.info("✅ Crawler setup completed")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to setup crawler: {e}")
            return False

    async def crawl_source(self, source: dict[str, Any]) -> list[dict]:
        """Crawl a specific source"""
        try:
            logger.info(f"🔍 Crawling {source['name']}...")

            # Set the current query on the crawler instance
            self.crawler.current_query = source["query"]

            # Navigate to the source URL
            await self.crawler.page.goto(source["url"])
            await asyncio.sleep(random.uniform(3, 5))  # Random delay

            # For Following/For You, we need to switch tabs
            if source["name"] in ["Following", "For You"]:
                try:
                    # Go to home page first
                    await self.crawler.page.goto("https://twitter.com/home")
                    await asyncio.sleep(3)

                    if source["name"] == "Following":
                        # Try to find and click the Following tab
                        try:
                            # Look for the Following tab in the timeline
                            following_tab = await self.crawler.page.query_selector(
                                'a[href="/home"][aria-selected="false"]'
                            )
                            if following_tab:
                                await following_tab.click()
                                await asyncio.sleep(2)
                            else:
                                # Try alternative selector
                                following_tab = await self.crawler.page.query_selector(
                                    'a[data-testid="AppTabBar_Home_Link"] + div a[href="/home"]'
                                )
                                if following_tab:
                                    await following_tab.click()
                                    await asyncio.sleep(2)
                        except Exception as e:
                            logger.warning(f"Could not find Following tab: {e}")
                    else:  # For You
                        # For You is usually the default, but let's make sure we're on the right tab
                        try:
                            # Look for the For You tab (usually the first tab)
                            for_you_tab = await self.crawler.page.query_selector(
                                'a[href="/home"][aria-selected="true"]'
                            )
                            if not for_you_tab:
                                # Try to click the first home tab
                                home_tab = await self.crawler.page.query_selector(
                                    'a[data-testid="AppTabBar_Home_Link"]'
                                )
                                if home_tab:
                                    await home_tab.click()
                                    await asyncio.sleep(2)
                        except Exception as e:
                            logger.warning(f"Could not find For You tab: {e}")
                except Exception as e:
                    logger.warning(f"Could not switch to {source['name']} tab: {e}")

            # Wait for content to load
            await asyncio.sleep(random.uniform(2, 4))

            # Extract tweets
            tweets = await self.crawler.extract_tweets_enhanced(
                source["tweets_per_source"]
            )

            # Add source metadata
            for tweet in tweets:
                tweet["source"] = source["name"]
                tweet["crawl_time"] = datetime.now().isoformat()

            logger.info(f"✅ Found {len(tweets)} tweets from {source['name']}")
            return tweets

        except Exception as e:
            logger.error(f"❌ Error crawling {source['name']}: {e}")
            return []

    async def save_and_upload_tweets(self, all_tweets: list[dict]):
        """Save tweets locally and upload to GCS"""
        if not all_tweets:
            logger.warning("No tweets to save")
            return

        try:
            # Save locally
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"continuous_crawl_{timestamp}.json"
            filepath = os.path.join("output", filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(all_tweets, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ Saved {len(all_tweets)} tweets to {filepath}")

            # Upload to GCS
            await self.crawler.save_tweets(all_tweets)
            logger.info(f"✅ Uploaded {len(all_tweets)} tweets to GCS")

        except Exception as e:
            logger.error(f"❌ Error saving tweets: {e}")

    async def run_crawl_cycle(self):
        """Run one complete crawl cycle across all sources"""
        logger.info("🚀 Starting crawl cycle...")

        all_tweets = []
        successful_sources = 0

        for source in self.crawl_sources:
            if not self.running:
                break

            try:
                tweets = await self.crawl_source(source)
                if tweets:
                    all_tweets.extend(tweets)
                    successful_sources += 1

                # Random delay between sources
                delay = random.uniform(10, 20)
                logger.info(f"⏳ Waiting {delay:.1f}s before next source...")
                await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"❌ Error in crawl cycle for {source['name']}: {e}")
                continue

        # Save and upload all collected tweets
        if all_tweets:
            await self.save_and_upload_tweets(all_tweets)
            logger.info(
                f"🎉 Crawl cycle completed: {len(all_tweets)} tweets from {successful_sources} sources"
            )
        else:
            logger.warning("❌ No tweets collected in this cycle")

    async def run_continuous(self):
        """Run the continuous crawler from 4 AM to 12 AM (20 hours/day)"""
        logger.info("🚀 Starting Continuous Twitter Crawler (4 AM - 12 AM daily)")

        if not await self.setup_crawler():
            logger.error("❌ Failed to setup crawler, exiting")
            return

        self.running = True
        cycle_count = 0

        try:
            while self.running:
                current_hour = datetime.now().hour
                
                # Check if we're in the active crawling window (4 AM to 12 AM)
                if 4 <= current_hour < 24:  # 4 AM to 11:59 PM
                    cycle_count += 1
                    logger.info(f"🔄 Starting cycle #{cycle_count} (Hour: {current_hour})")

                    start_time = time.time()
                    await self.run_crawl_cycle()
                    cycle_duration = time.time() - start_time

                    logger.info(f"⏱️ Cycle #{cycle_count} took {cycle_duration:.1f} seconds")

                    # Shorter wait time during active hours (30 minutes between cycles)
                    # This gives us more frequent crawling during the day
                    wait_time = 30 * 60  # 30 minutes
                    logger.info(
                        f"😴 Sleeping for {wait_time/60:.1f} minutes before next cycle..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    # Outside active hours (12 AM to 4 AM) - sleep longer
                    logger.info(f"🌙 Outside active hours (Hour: {current_hour}). Sleeping until 4 AM...")
                    
                    # Calculate time until 4 AM
                    now = datetime.now()
                    if current_hour < 4:
                        # It's between 12 AM and 4 AM, wait until 4 AM
                        target_time = now.replace(hour=4, minute=0, second=0, microsecond=0)
                    else:
                        # It's after 12 AM, wait until next day 4 AM
                        target_time = (now + timedelta(days=1)).replace(hour=4, minute=0, second=0, microsecond=0)
                    
                    sleep_seconds = (target_time - now).total_seconds()
                    logger.info(f"😴 Sleeping for {sleep_seconds/3600:.1f} hours until 4 AM...")
                    await asyncio.sleep(sleep_seconds)

        except KeyboardInterrupt:
            logger.info("🛑 Received interrupt signal, stopping crawler...")
        except Exception as e:
            logger.error(f"❌ Unexpected error in continuous crawler: {e}")
        finally:
            self.running = False
            if self.crawler:
                await self.crawler.cleanup()
            logger.info("👋 Continuous crawler stopped")


async def main():
    """Main entry point"""
    crawler = ContinuousTwitterCrawler()
    await crawler.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())
