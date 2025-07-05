#!/usr/bin/env python3
"""
Standalone Crypto Crawler Service
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


class CryptoCrawler:
    def __init__(self):
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

    def upload_to_gcs(self, data: dict[str, Any]):
        """Upload data to GCS"""
        client, bucket = self.get_gcs_client()
        if not bucket:
            return False

        try:
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crypto_data/crypto_{timestamp}.json"

            # Upload data
            blob = bucket.blob(filename)
            blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            # Also upload as latest
            latest_filename = "crypto_data/crypto_latest.json"
            latest_blob = bucket.blob(latest_filename)
            latest_blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            logger.info(f"✅ Uploaded crypto data to GCS: {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload crypto data to GCS: {e}")
            return False

    async def crawl_crypto(self) -> dict[str, Any]:
        """Crawl crypto data from multiple sources"""
        try:
            logger.info("🔄 Starting Crypto crawl...")

            import requests

            all_gainers = []

            # CoinGecko Top Gainers
            try:
                logger.info("  🔄 Fetching CoinGecko top gainers...")
                coingecko_url = "https://api.coingecko.com/api/v3/coins/markets"
                params = {
                    "vs_currency": "usd",
                    "order": "price_change_percentage_24h_desc",
                    "per_page": 20,
                    "page": 1,
                    "sparkline": False,
                    "price_change_percentage": "24h",
                }

                response = requests.get(coingecko_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    gainers = []

                    for coin in data[:10]:  # Top 10 gainers
                        gainers.append(
                            {
                                "name": coin.get("name", ""),
                                "symbol": coin.get("symbol", "").upper(),
                                "price": coin.get("current_price", 0),
                                "price_change_24h": coin.get("price_change_24h", 0),
                                "price_change_percentage_24h": coin.get(
                                    "price_change_percentage_24h", 0
                                ),
                                "market_cap": coin.get("market_cap", 0),
                                "volume_24h": coin.get("total_volume", 0),
                                "source": "coingecko",
                            }
                        )

                    all_gainers.extend(gainers)
                    logger.info(f"  ✅ CoinGecko: {len(gainers)} gainers")
                else:
                    logger.warning(f"  ⚠️ CoinGecko API returned {response.status_code}")

            except Exception as e:
                logger.warning(f"  ⚠️ Failed to fetch CoinGecko data: {e}")

            # DEX Screener Trending
            try:
                logger.info("  🔄 Fetching DEX Screener trending...")
                dexscreener_url = (
                    "https://api.dexscreener.com/latest/dex/tokens/trending"
                )

                response = requests.get(dexscreener_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    trending = []

                    if "pairs" in data:
                        for pair in data["pairs"][:5]:  # Top 5 trending
                            trending.append(
                                {
                                    "name": pair.get("baseToken", {}).get("name", ""),
                                    "symbol": pair.get("baseToken", {}).get(
                                        "symbol", ""
                                    ),
                                    "price": float(pair.get("priceUsd", 0)),
                                    "price_change_24h": float(
                                        pair.get("priceChange", {}).get("h24", 0)
                                    ),
                                    "volume_24h": float(
                                        pair.get("volume", {}).get("h24", 0)
                                    ),
                                    "liquidity": float(
                                        pair.get("liquidity", {}).get("usd", 0)
                                    ),
                                    "dex": pair.get("dexId", ""),
                                    "chain": pair.get("chainId", ""),
                                    "source": "dexscreener",
                                }
                            )

                    all_gainers.extend(trending)
                    logger.info(f"  ✅ DEX Screener: {len(trending)} trending")
                else:
                    logger.warning(
                        f"  ⚠️ DEX Screener API returned {response.status_code}"
                    )

            except Exception as e:
                logger.warning(f"  ⚠️ Failed to fetch DEX Screener data: {e}")

            # DexPaprika Trending
            try:
                logger.info("  🔄 Fetching DexPaprika trending...")
                dexpaprika_url = "https://api.dexpaprika.com/v1/trending"

                response = requests.get(dexpaprika_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    trending = []

                    if "data" in data:
                        for item in data["data"][:5]:  # Top 5 trending
                            trending.append(
                                {
                                    "name": item.get("name", ""),
                                    "symbol": item.get("symbol", ""),
                                    "price": float(item.get("price", 0)),
                                    "price_change_24h": float(
                                        item.get("price_change_24h", 0)
                                    ),
                                    "volume_24h": float(item.get("volume_24h", 0)),
                                    "market_cap": float(item.get("market_cap", 0)),
                                    "chain": item.get("chain", ""),
                                    "source": "dexpaprika",
                                }
                            )

                    all_gainers.extend(trending)
                    logger.info(f"  ✅ DexPaprika: {len(trending)} trending")
                else:
                    logger.warning(
                        f"  ⚠️ DexPaprika API returned {response.status_code}"
                    )

            except Exception as e:
                logger.warning(f"  ⚠️ Failed to fetch DexPaprika data: {e}")

            data = {
                "gainers": all_gainers,
                "metadata": {
                    "source": "crypto",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": len(all_gainers),
                    "status": "success",
                    "sources": ["coingecko", "dexscreener", "dexpaprika"],
                },
            }

            logger.info(f"✅ Crypto crawl completed: {len(all_gainers)} items")
            return data

        except Exception as e:
            logger.error(f"❌ Crypto crawl failed: {e}")
            return {
                "gainers": [],
                "metadata": {
                    "source": "crypto",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "count": 0,
                    "status": "error",
                    "error": str(e),
                },
            }

    async def run_single_crawl(self):
        """Run a single Crypto crawl session"""
        logger.info("🔄 Running Crypto crawl session...")

        # Crawl Crypto
        crypto_data = await self.crawl_crypto()

        # Upload to GCS
        if self.upload_to_gcs(crypto_data):
            logger.info("✅ Crypto crawl session completed successfully")
        else:
            logger.error("❌ Failed to upload Crypto data")

        return crypto_data


async def main():
    """Main function for standalone Crypto crawler"""
    crawler = CryptoCrawler()

    # Run single crawl
    result = await crawler.run_single_crawl()

    logger.info("📊 Crawl Summary:")
    logger.info(f"  - Crypto: {len(result['gainers'])} items")

    return result


if __name__ == "__main__":
    asyncio.run(main())
