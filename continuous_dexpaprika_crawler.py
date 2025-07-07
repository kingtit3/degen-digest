#!/usr/bin/env python3
"""
Continuous DexPaprika Crawler - Runs independently
Fetches token data from multiple networks
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
        logging.FileHandler("output/continuous_dexpaprika.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ContinuousDexPaprikaCrawler:
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
            timestamped_path = f"data/dexpaprika_{timestamp}.json"
            blob = bucket.blob(timestamped_path)
            blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            # Upload latest file
            latest_path = "data/dexpaprika_latest.json"
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

    def crawl_dexpaprika(self) -> dict[str, Any]:
        """Crawl DexPaprika data"""
        try:
            logger.info("🔄 Starting DexPaprika crawl...")

            # Import the DexPaprika scraper
            from scrapers.dexpaprika import (
                fetch_networks,
                fetch_token_data,
                fetch_token_prices,
            )

            # Example Solana tokens to track
            solana_tokens = [
                "So11111111111111111111111111111111111111112",  # SOL
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
                "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
                "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",  # POPCAT
            ]

            network_id = "solana"

            data = {
                "metadata": {
                    "source": "dexpaprika",
                    "fetched_at": datetime.now().isoformat(),
                    "network": network_id,
                    "tokens_tracked": len(solana_tokens),
                },
                "networks": fetch_networks(),
                "token_data": fetch_token_prices(network_id, solana_tokens),
                "summary": {
                    "total_tokens": len(solana_tokens),
                    "network_id": network_id,
                    "api_version": "v1",
                },
            }

            # Save locally
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dexpaprika_continuous_{timestamp}.json"
            filepath = os.path.join("output", filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ Saved {filename} locally")
            logger.info(
                f"✅ DexPaprika crawl completed: {len(data['token_data'])} tokens"
            )

            return data

        except Exception as e:
            logger.error(f"❌ DexPaprika crawl failed: {e}")
            return {
                "metadata": {
                    "source": "dexpaprika",
                    "fetched_at": datetime.now().isoformat(),
                    "status": "error",
                    "error": str(e),
                },
                "networks": [],
                "token_data": [],
                "summary": {},
            }

    async def run_crawl_cycle(self):
        """Run one complete DexPaprika crawl cycle"""
        logger.info("🚀 Starting DexPaprika crawl cycle...")

        try:
            # Crawl DexPaprika data
            data = self.crawl_dexpaprika()

            # Upload to GCS
            if self.upload_to_gcs(data):
                logger.info("✅ DexPaprika cycle completed successfully")
            else:
                logger.error("❌ Failed to upload DexPaprika data")

        except Exception as e:
            logger.error(f"❌ Error in DexPaprika crawl cycle: {e}")

    async def run_continuous(self):
        """Run the continuous DexPaprika crawler"""
        logger.info("🚀 Starting Continuous DexPaprika Crawler")

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

                # Wait before next cycle (7 minutes between cycles = 12 cycles per day)
                wait_time = 7 * 60  # 7 minutes
                logger.info(
                    f"😴 Sleeping for {wait_time/60:.1f} minutes before next cycle..."
                )
                await asyncio.sleep(wait_time)

        except KeyboardInterrupt:
            logger.info("🛑 Received interrupt signal, stopping crawler...")
        except Exception as e:
            logger.error(f"❌ Unexpected error in continuous DexPaprika crawler: {e}")
        finally:
            self.running = False
            logger.info("👋 Continuous DexPaprika crawler stopped")


async def main():
    """Main entry point"""
    crawler = ContinuousDexPaprikaCrawler()
    await crawler.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())
