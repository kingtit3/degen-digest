#!/usr/bin/env python3
"""
Minimal test crawler without Twitter imports
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


class MinimalCrawler:
    def __init__(self):
        self.output_dir = Path("/tmp")
        self.output_dir.mkdir(exist_ok=True)

        # Cloud configuration
        self.gcs_bucket = "degen-digest-data"
        self.project_id = "lucky-union-463615-t3"

        # Crawler state
        self.is_running = False

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
        """Run a single crawl session"""
        try:
            logger.info("Starting minimal crawl session...")

            # Only crypto crawl for now
            crypto_data = self.crawl_crypto_simple()
            logger.info(f"  - Crypto: {len(crypto_data.get('gainers', []))} gainers")

            logger.info("Minimal crawl session successful!")
            return True

        except Exception as e:
            logger.error(f"Minimal crawl session failed: {e}")
            return False

    async def run_continuous_crawler(self):
        """Main continuous crawler loop"""
        self.is_running = True

        logger.info("🚀 Starting Minimal Crawler...")
        logger.info("📅 Active hours: 6:00 - 0:00")
        logger.info("⏰ Crawl interval: 30 minutes")

        while self.is_running:
            try:
                # Check if we're in active hours
                now = datetime.now()
                current_hour = now.hour

                # Active hours: 6 AM to 12 AM
                is_active = current_hour >= 6

                if is_active:
                    logger.info(
                        f"🔄 Running minimal crawl session at {now.strftime('%H:%M:%S')}"
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
        logger.info("👋 Minimal crawler stopped")


async def main():
    """Main function"""
    # Create crawler
    crawler = MinimalCrawler()

    # Run the crawler
    await crawler.run_continuous_crawler()


if __name__ == "__main__":
    asyncio.run(main())
