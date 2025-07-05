#!/usr/bin/env python3
"""
Continuous DexScreener Crawler - Runs independently
Fetches trending tokens, boosted tokens, and token pairs
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("output/continuous_dexscreener.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ContinuousDexScreenerCrawler:
    def __init__(self):
        self.running = False
        self.gcs_bucket = "degen-digest-data"
        self.project_id = "lucky-union-463615-t3"

        # Import GCS functionality
        try:
            from google.cloud import storage

            self.storage = storage
            self.gcs_available = True
        except ImportError:
            logger.warning("Google Cloud Storage not available")
            self.gcs_available = False

    def get_gcs_client(self):
        """Get GCS client if available"""
        if not self.gcs_available:
            return None, None

        try:
            client = self.storage.Client(project=self.project_id)
            bucket = client.bucket(self.gcs_bucket)
            return client, bucket
        except Exception as e:
            logger.error(f"GCS connection failed: {e}")
            return None, None

    def upload_to_gcs(self, data: dict[str, Any]) -> bool:
        """Upload data to Google Cloud Storage"""
        client, bucket = self.get_gcs_client()
        if not bucket:
            logger.warning("GCS not available, skipping upload")
            return False

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Upload timestamped file
            timestamped_path = f"data/dexscreener_{timestamp}.json"
            blob = bucket.blob(timestamped_path)
            blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            # Upload latest file
            latest_path = "data/dexscreener_latest.json"
            blob = bucket.blob(latest_path)
            blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            logger.info(f"✅ Uploaded to GCS: {timestamped_path} and {latest_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload to GCS: {e}")
            return False

    def crawl_dexscreener(self) -> dict[str, Any]:
        """Crawl DexScreener data"""
        try:
            logger.info("🔄 Starting DexScreener crawl...")

            # Import the DexScreener scraper
            from scrapers.dexscreener import (
                fetch_latest_boosted_tokens,
                fetch_latest_token_profiles,
                fetch_pair_by_id,
                fetch_search_pairs,
                fetch_token_pairs,
                fetch_tokens_by_address,
                fetch_top_boosted_tokens,
            )

            # Example Solana token and pair for demonstration
            solana_token = "So11111111111111111111111111111111111111112"
            usdc_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            example_pair_id = (
                "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN"  # Jupiter SOL/USDC
            )
            chain_id = "solana"

            data = {
                "latest_token_profiles": fetch_latest_token_profiles(),
                "latest_boosted_tokens": fetch_latest_boosted_tokens(),
                "top_boosted_tokens": fetch_top_boosted_tokens(),
                "token_pairs": fetch_token_pairs(chain_id, solana_token),
                "tokens_by_address": fetch_tokens_by_address(
                    chain_id, f"{solana_token},{usdc_token}"
                ),
                "pair_by_id": fetch_pair_by_id(chain_id, example_pair_id),
                "search_pairs": fetch_search_pairs("SOL/USDC"),
                "metadata": {
                    "source": "dexscreener",
                    "crawled_at": datetime.now().isoformat(),
                    "status": "success",
                    "chain_id": chain_id,
                    "tokens_tracked": [solana_token, usdc_token],
                },
            }

            # Save locally
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dexscreener_continuous_{timestamp}.json"
            filepath = os.path.join("output", filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ Saved {filename} locally")
            logger.info(
                f"✅ DexScreener crawl completed: {len(data.get('latest_token_profiles', []))} token profiles"
            )

            return data

        except Exception as e:
            logger.error(f"❌ DexScreener crawl failed: {e}")
            return {
                "latest_token_profiles": [],
                "latest_boosted_tokens": [],
                "top_boosted_tokens": [],
                "token_pairs": [],
                "tokens_by_address": [],
                "pair_by_id": {},
                "search_pairs": [],
                "metadata": {
                    "source": "dexscreener",
                    "crawled_at": datetime.now().isoformat(),
                    "status": "error",
                    "error": str(e),
                },
            }

    async def run_crawl_cycle(self):
        """Run one complete DexScreener crawl cycle"""
        logger.info("🚀 Starting DexScreener crawl cycle...")

        try:
            # Crawl DexScreener data
            data = self.crawl_dexscreener()

            # Upload to GCS
            if self.upload_to_gcs(data):
                logger.info("✅ DexScreener cycle completed successfully")
            else:
                logger.error("❌ Failed to upload DexScreener data")

        except Exception as e:
            logger.error(f"❌ Error in DexScreener crawl cycle: {e}")

    async def run_continuous(self):
        """Run the continuous DexScreener crawler"""
        logger.info("🚀 Starting Continuous DexScreener Crawler")

        self.running = True
        cycle_count = 0

        try:
            while self.running:
                cycle_count += 1
                logger.info(f"🔄 Starting cycle #{cycle_count}")

                start_time = time.time()
                await self.run_crawl_cycle()
                cycle_duration = time.time() - start_time

                logger.info(f"⏱️ Cycle #{cycle_count} took {cycle_duration:.1f} seconds")

                # Wait before next cycle (2 hours between cycles = 12 cycles per day)
                wait_time = 2 * 60 * 60  # 2 hours
                logger.info(
                    f"😴 Sleeping for {wait_time/3600:.1f} hours before next cycle..."
                )
                await asyncio.sleep(wait_time)

        except KeyboardInterrupt:
            logger.info("🛑 Received interrupt signal, stopping crawler...")
        except Exception as e:
            logger.error(f"❌ Unexpected error in continuous DexScreener crawler: {e}")
        finally:
            self.running = False
            logger.info("👋 Continuous DexScreener crawler stopped")


async def main():
    """Main entry point"""
    crawler = ContinuousDexScreenerCrawler()
    await crawler.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())
