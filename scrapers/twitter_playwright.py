#!/usr/bin/env python3
"""
Twitter Crawler using Playwright
Continuously searches Twitter for crypto content and explores narratives
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright
from textblob import TextBlob

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterPlaywrightCrawler:
    def __init__(self, headless: bool = True, output_dir: str = "output"):
        self.headless = headless
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.browser = None
        self.page = None

        # Search queries for crypto content
        self.search_queries = [
            "crypto",
            "bitcoin",
            "ethereum",
            "altcoin",
            "defi",
            "nft",
            "moon",
            "pump",
            "dump",
            "hodl",
            "fomo",
            "rug pull",
            "meme coin",
            "solana",
            "cardano",
            "polkadot",
            "chainlink",
            "uniswap",
            "pancakeswap",
            "binance",
        ]

        # User agents to rotate
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]

    async def setup_browser(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()

        # Launch browser with stealth settings
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
            ],
        )

        # Create context with stealth settings
        context = await self.browser.new_context(
            user_agent=random.choice(self.user_agents),
            viewport={"width": 1920, "height": 1080},
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        self.page = await context.new_page()

        # Add stealth scripts
        await self.page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """
        )

    async def search_twitter(
        self, query: str, max_tweets: int = 50
    ) -> list[dict[str, Any]]:
        """Search Twitter for a specific query"""
        logger.info(f"Searching Twitter for: {query}")

        try:
            # Navigate to Twitter search
            search_url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
            await self.page.goto(search_url, wait_until="networkidle")

            # Wait for tweets to load
            await self.page.wait_for_selector(
                'article[data-testid="tweet"]', timeout=10000
            )

            # Scroll to load more tweets
            tweets_loaded = 0
            max_scrolls = 10

            for scroll in range(max_scrolls):
                if tweets_loaded >= max_tweets:
                    break

                # Scroll down
                await self.page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(2)

                # Count current tweets
                tweet_elements = await self.page.query_selector_all(
                    'article[data-testid="tweet"]'
                )
                tweets_loaded = len(tweet_elements)

                logger.info(
                    f"Loaded {tweets_loaded} tweets for '{query}' (scroll {scroll + 1})"
                )

            # Extract tweet data
            tweets = await self.extract_tweets(max_tweets)
            logger.info(f"Extracted {len(tweets)} tweets for '{query}'")

            return tweets

        except Exception as e:
            logger.error(f"Error searching Twitter for '{query}': {e}")
            return []

    async def extract_tweets(self, max_tweets: int) -> list[dict[str, Any]]:
        """Extract tweet data from the current page"""
        tweets = []

        try:
            # Get all tweet articles
            tweet_elements = await self.page.query_selector_all(
                'article[data-testid="tweet"]'
            )

            for i, tweet_element in enumerate(tweet_elements[:max_tweets]):
                try:
                    tweet_data = await self.extract_single_tweet(tweet_element)
                    if tweet_data:
                        tweets.append(tweet_data)
                except Exception as e:
                    logger.warning(f"Error extracting tweet {i}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting tweets: {e}")

        return tweets

    async def extract_single_tweet(self, tweet_element) -> dict[str, Any] | None:
        """Extract data from a single tweet element"""
        try:
            # Extract tweet text
            text_element = await tweet_element.query_selector(
                '[data-testid="tweetText"]'
            )
            text = await text_element.inner_text() if text_element else ""

            if not text.strip():
                return None

            # Extract username
            username_element = await tweet_element.query_selector('a[role="link"]')
            username = (
                await username_element.get_attribute("href") if username_element else ""
            )
            if username and username.startswith("/"):
                username = username[1:]  # Remove leading slash

            # Extract timestamp
            time_element = await tweet_element.query_selector("time")
            timestamp = (
                await time_element.get_attribute("datetime") if time_element else ""
            )

            # Extract engagement metrics (approximate)
            engagement = await self.extract_engagement(tweet_element)

            # Analyze sentiment
            sentiment = self.analyze_sentiment(text)

            # Create tweet object
            tweet_data = {
                "source": "twitter_playwright",
                "id": f"playwright_{int(time.time())}_{hash(text)}",
                "text": text,
                "username": username,
                "created_at": timestamp or datetime.now(timezone.utc).isoformat(),
                "engagement": engagement,
                "sentiment": sentiment,
                "query": getattr(self, "current_query", "unknown"),
                "collected_at": datetime.now(timezone.utc).isoformat(),
            }

            return tweet_data

        except Exception as e:
            logger.warning(f"Error extracting single tweet: {e}")
            return None

    async def extract_engagement(self, tweet_element) -> dict[str, int]:
        """Extract engagement metrics from tweet"""
        engagement = {"likes": 0, "retweets": 0, "replies": 0, "views": 0}

        try:
            # Look for engagement buttons
            like_button = await tweet_element.query_selector('[data-testid="like"]')
            retweet_button = await tweet_element.query_selector(
                '[data-testid="retweet"]'
            )
            reply_button = await tweet_element.query_selector('[data-testid="reply"]')

            # Extract counts (this is approximate as Twitter doesn't always show exact numbers)
            if like_button:
                like_text = await like_button.inner_text()
                engagement["likes"] = self.parse_engagement_count(like_text)

            if retweet_button:
                retweet_text = await retweet_button.inner_text()
                engagement["retweets"] = self.parse_engagement_count(retweet_text)

            if reply_button:
                reply_text = await reply_button.inner_text()
                engagement["replies"] = self.parse_engagement_count(reply_text)

        except Exception as e:
            logger.warning(f"Error extracting engagement: {e}")

        return engagement

    def parse_engagement_count(self, text: str) -> int:
        """Parse engagement count from text (e.g., '1.2K' -> 1200)"""
        if not text or text.strip() == "":
            return 0

        text = text.strip().lower()

        try:
            if "k" in text:
                return int(float(text.replace("k", "")) * 1000)
            elif "m" in text:
                return int(float(text.replace("m", "")) * 1000000)
            else:
                return int(text)
        except Exception:
            return 0

    def analyze_sentiment(self, text: str) -> dict[str, float]:
        """Analyze sentiment of tweet text"""
        try:
            blob = TextBlob(text)
            return {
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity,
            }
        except Exception:
            return {"polarity": 0.0, "subjectivity": 0.0}

    async def crawl_continuously(
        self, interval_minutes: int = 5, max_tweets_per_query: int = 30
    ):
        """Continuously crawl Twitter for all search queries"""
        logger.info(
            f"Starting continuous Twitter crawl (interval: {interval_minutes} minutes)"
        )

        await self.setup_browser()

        try:
            while True:
                start_time = time.time()
                all_tweets = []

                # Search for each query
                for query in self.search_queries:
                    self.current_query = query
                    tweets = await self.search_twitter(query, max_tweets_per_query)
                    all_tweets.extend(tweets)

                    # Random delay between queries to avoid rate limiting
                    await asyncio.sleep(random.uniform(2, 5))

                # Save collected tweets
                if all_tweets:
                    await self.save_tweets(all_tweets)

                # Calculate time to next crawl
                elapsed = time.time() - start_time
                sleep_time = max(0, (interval_minutes * 60) - elapsed)

                logger.info(
                    f"Crawl completed: {len(all_tweets)} tweets collected. Next crawl in {sleep_time/60:.1f} minutes"
                )

                await asyncio.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("Crawling stopped by user")
        except Exception as e:
            logger.error(f"Error in continuous crawl: {e}")
        finally:
            await self.cleanup()

    async def save_tweets(self, tweets: list[dict[str, Any]]):
        """Save tweets to file and database"""
        try:
            # Save to JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"twitter_playwright_{timestamp}.json"
            filepath = self.output_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(tweets, f, indent=2, default=str)

            # Also save to consolidated file
            consolidated_file = self.output_dir / "twitter_playwright_latest.json"
            with open(consolidated_file, "w", encoding="utf-8") as f:
                json.dump(tweets, f, indent=2, default=str)

            logger.info(f"Saved {len(tweets)} tweets to {filepath}")

            # TODO: Save to database if needed
            # await self.save_to_database(tweets)

        except Exception as e:
            logger.error(f"Error saving tweets: {e}")

    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, "playwright"):
            await self.playwright.stop()


async def main():
    """Main function to run the Twitter crawler"""
    crawler = TwitterPlaywrightCrawler(headless=True)

    # Run continuous crawl
    await crawler.crawl_continuously(interval_minutes=5, max_tweets_per_query=20)


if __name__ == "__main__":
    asyncio.run(main())
