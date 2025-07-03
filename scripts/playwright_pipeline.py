#!/usr/bin/env python3
"""
Playwright Twitter Crawler Pipeline Integration
Integrates the Playwright crawler into the existing Degen Digest pipeline
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.twitter_playwright import TwitterPlaywrightCrawler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaywrightPipeline:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.crawler = None

    async def run_single_crawl(
        self, max_tweets_per_query: int = 20
    ) -> list[dict[str, Any]]:
        """Run a single crawl session"""
        logger.info("Starting Playwright Twitter crawl session...")

        self.crawler = TwitterPlaywrightCrawler(
            headless=True, output_dir=str(self.output_dir)
        )

        try:
            await self.crawler.setup_browser()

            all_tweets = []

            # Search for each query
            for query in self.crawler.search_queries[
                :5
            ]:  # Limit to 5 queries for testing
                logger.info(f"Searching for: {query}")
                tweets = await self.crawler.search_twitter(query, max_tweets_per_query)
                all_tweets.extend(tweets)

                # Small delay between queries
                await asyncio.sleep(2)

            # Save results
            if all_tweets:
                await self.crawler.save_tweets(all_tweets)
                await self.merge_with_existing_data(all_tweets)

            logger.info(f"Crawl session completed: {len(all_tweets)} tweets collected")
            return all_tweets

        except Exception as e:
            logger.error(f"Error in crawl session: {e}")
            return []
        finally:
            if self.crawler:
                await self.crawler.cleanup()

    async def merge_with_existing_data(self, new_tweets: list[dict[str, Any]]):
        """Merge new tweets with existing data"""
        try:
            # Load existing consolidated data
            consolidated_file = self.output_dir / "consolidated_data.json"

            if consolidated_file.exists():
                with open(consolidated_file, encoding="utf-8") as f:
                    existing_data = json.load(f)
            else:
                existing_data = {
                    "tweets": [],
                    "reddit_posts": [],
                    "telegram_messages": [],
                    "news_articles": [],
                    "metadata": {
                        "last_updated": datetime.now(timezone.utc).isoformat(),
                        "total_items": 0,
                        "sources": [],
                    },
                }

            # Add new tweets
            existing_data["tweets"].extend(new_tweets)

            # Update metadata
            existing_data["metadata"]["last_updated"] = datetime.now(
                timezone.utc
            ).isoformat()
            existing_data["metadata"]["total_items"] = len(existing_data["tweets"])

            # Save updated data
            with open(consolidated_file, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=2, default=str)

            logger.info(f"Merged {len(new_tweets)} new tweets with existing data")

        except Exception as e:
            logger.error(f"Error merging data: {e}")

    async def run_continuous_pipeline(self, interval_minutes: int = 10):
        """Run continuous pipeline with Playwright crawler"""
        logger.info(
            f"Starting continuous Playwright pipeline (interval: {interval_minutes} minutes)"
        )

        while True:
            try:
                start_time = datetime.now()

                # Run crawl session
                tweets = await self.run_single_crawl()

                # Calculate next run time
                elapsed = (datetime.now() - start_time).total_seconds()
                sleep_time = max(0, (interval_minutes * 60) - elapsed)

                logger.info(
                    f"Pipeline cycle completed. Next run in {sleep_time/60:.1f} minutes"
                )

                await asyncio.sleep(sleep_time)

            except KeyboardInterrupt:
                logger.info("Pipeline stopped by user")
                break
            except Exception as e:
                logger.error(f"Pipeline error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying


async def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Playwright Twitter Crawler Pipeline")
    parser.add_argument(
        "--mode",
        choices=["single", "continuous"],
        default="single",
        help="Run mode: single crawl or continuous pipeline",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Interval between crawls in minutes (continuous mode)",
    )
    parser.add_argument(
        "--max-tweets", type=int, default=20, help="Maximum tweets per query"
    )

    args = parser.parse_args()

    pipeline = PlaywrightPipeline()

    if args.mode == "single":
        await pipeline.run_single_crawl(args.max_tweets)
    else:
        await pipeline.run_continuous_pipeline(args.interval)


if __name__ == "__main__":
    asyncio.run(main())
