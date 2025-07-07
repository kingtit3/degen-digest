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
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Add current directory to path
sys.path.append(".")

# Import advanced logging
try:
    from utils.advanced_logging import get_logger, configure_logging
    configure_logging(level="DEBUG")
    logger = get_logger("dexscreener.crawler")
except ImportError:
    # Fallback to basic logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("output/continuous_dexscreener.log"),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger("dexscreener.crawler")

# Add performance monitoring
import time
from functools import wraps

def log_performance(func):
    """Decorator to log function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                "Function completed",
                function=func.__name__,
                duration_seconds=duration,
                status="success"
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Function failed",
                function=func.__name__,
                duration_seconds=duration,
                error=str(e),
                traceback=traceback.format_exc(),
                status="error"
            )
            raise
    return wrapper


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

    @log_performance
    def upload_to_gcs(self, data: dict[str, Any]) -> bool:
        """Upload data to Google Cloud Storage with detailed logging"""
        logger.info(
            "Starting GCS upload",
            component="upload",
            operation="upload_to_gcs",
            data_size=len(json.dumps(data)),
            bucket=self.gcs_bucket
        )
        
        client, bucket = self.get_gcs_client()
        if not bucket:
            logger.warning(
                "GCS not available, skipping upload",
                component="upload",
                operation="upload_to_gcs"
            )
            return False

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_json = json.dumps(data, indent=2, ensure_ascii=False)
            data_size = len(data_json)

            logger.debug(
                "Preparing GCS upload",
                timestamp=timestamp,
                data_size_bytes=data_size,
                data_size_mb=data_size / (1024 * 1024)
            )

            # Upload timestamped file
            timestamped_path = f"data/dexscreener_{timestamp}.json"
            blob = bucket.blob(timestamped_path)
            blob.upload_from_string(
                data_json,
                content_type="application/json",
            )

            logger.info(
                "Uploaded timestamped file to GCS",
                path=timestamped_path,
                size_bytes=data_size
            )

            # Upload latest file
            latest_path = "data/dexscreener_latest.json"
            blob = bucket.blob(latest_path)
            blob.upload_from_string(
                data_json,
                content_type="application/json",
            )

            logger.info(
                "Uploaded latest file to GCS",
                path=latest_path,
                size_bytes=data_size
            )

            logger.info(
                "GCS upload completed successfully",
                files_uploaded=[timestamped_path, latest_path],
                total_size_bytes=data_size * 2,
                bucket=self.gcs_bucket
            )
            return True

        except Exception as e:
            logger.error(
                "Failed to upload to GCS",
                error=str(e),
                traceback=traceback.format_exc(),
                component="upload",
                operation="upload_to_gcs",
                bucket=self.gcs_bucket
            )
            return False

    @log_performance
    def crawl_dexscreener(self) -> dict[str, Any]:
        """Crawl DexScreener data with comprehensive logging"""
        logger.info(
            "Starting DexScreener crawl",
            component="crawler",
            operation="crawl_dexscreener",
            timestamp=datetime.now().isoformat()
        )
        
        try:
            # Import the DexScreener scraper
            logger.debug("Importing DexScreener scraper modules")
            from scrapers.dexscreener import (
                fetch_latest_boosted_tokens,
                fetch_latest_token_profiles,
                fetch_pair_by_id,
                fetch_search_pairs,
                fetch_token_pairs,
                fetch_tokens_by_address,
                fetch_top_boosted_tokens,
            )
            logger.debug("Successfully imported DexScreener scraper modules")

            # Example Solana token and pair for demonstration
            solana_token = "So11111111111111111111111111111111111111112"
            usdc_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            example_pair_id = (
                "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN"  # Jupiter SOL/USDC
            )
            chain_id = "solana"

            logger.info(
                "Fetching DexScreener data",
                tokens=[solana_token, usdc_token],
                chain_id=chain_id,
                pair_id=example_pair_id
            )

            # Fetch data with detailed logging
            logger.debug("Fetching latest token profiles")
            latest_token_profiles = fetch_latest_token_profiles()
            logger.info(
                "Fetched latest token profiles",
                count=len(latest_token_profiles),
                sample_tokens=[t.get('name', 'Unknown')[:3] for t in latest_token_profiles[:3]]
            )

            logger.debug("Fetching latest boosted tokens")
            latest_boosted_tokens = fetch_latest_boosted_tokens()
            logger.info(
                "Fetched latest boosted tokens",
                count=len(latest_boosted_tokens)
            )

            logger.debug("Fetching top boosted tokens")
            top_boosted_tokens = fetch_top_boosted_tokens()
            logger.info(
                "Fetched top boosted tokens",
                count=len(top_boosted_tokens)
            )

            logger.debug("Fetching token pairs")
            token_pairs = fetch_token_pairs(chain_id, solana_token)
            logger.info(
                "Fetched token pairs",
                count=len(token_pairs),
                chain_id=chain_id,
                token=solana_token
            )

            logger.debug("Fetching tokens by address")
            tokens_by_address = fetch_tokens_by_address(
                chain_id, f"{solana_token},{usdc_token}"
            )
            logger.info(
                "Fetched tokens by address",
                count=len(tokens_by_address),
                addresses=[solana_token, usdc_token]
            )

            logger.debug("Fetching pair by ID")
            pair_by_id = fetch_pair_by_id(chain_id, example_pair_id)
            logger.info(
                "Fetched pair by ID",
                pair_id=example_pair_id,
                has_data=bool(pair_by_id)
            )

            logger.debug("Fetching search pairs")
            search_pairs = fetch_search_pairs("SOL/USDC")
            logger.info(
                "Fetched search pairs",
                count=len(search_pairs),
                query="SOL/USDC"
            )

            data = {
                "latest_token_profiles": latest_token_profiles,
                "latest_boosted_tokens": latest_boosted_tokens,
                "top_boosted_tokens": top_boosted_tokens,
                "token_pairs": token_pairs,
                "tokens_by_address": tokens_by_address,
                "pair_by_id": pair_by_id,
                "search_pairs": search_pairs,
                "metadata": {
                    "source": "dexscreener",
                    "crawled_at": datetime.now().isoformat(),
                    "status": "success",
                    "chain_id": chain_id,
                    "tokens_tracked": [solana_token, usdc_token],
                    "total_items": len(latest_token_profiles) + len(latest_boosted_tokens) + len(top_boosted_tokens),
                },
            }

            logger.info(
                "DexScreener data collection completed",
                total_token_profiles=len(latest_token_profiles),
                total_boosted_tokens=len(latest_boosted_tokens),
                total_top_boosted=len(top_boosted_tokens),
                total_pairs=len(token_pairs),
                total_search_results=len(search_pairs)
            )

            # Save locally with detailed logging
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dexscreener_continuous_{timestamp}.json"
            filepath = os.path.join("output", filename)

            logger.debug("Saving data to local file", filepath=filepath)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            file_size = os.path.getsize(filepath)
            logger.info(
                "Saved DexScreener data locally",
                filename=filename,
                file_size_bytes=file_size,
                file_size_mb=file_size / (1024 * 1024)
            )

            return data

        except Exception as e:
            logger.error(
                "DexScreener crawl failed",
                error=str(e),
                traceback=traceback.format_exc(),
                component="crawler",
                operation="crawl_dexscreener"
            )
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
                    "traceback": traceback.format_exc(),
                },
            }

    @log_performance
    async def run_crawl_cycle(self):
        """Run one complete DexScreener crawl cycle with detailed logging"""
        logger.info(
            "Starting DexScreener crawl cycle",
            component="cycle",
            operation="run_crawl_cycle",
            timestamp=datetime.now().isoformat()
        )

        try:
            # Crawl DexScreener data
            logger.debug("Starting data crawling phase")
            data = self.crawl_dexscreener()
            
            logger.info(
                "Data crawling completed",
                data_keys=list(data.keys()),
                metadata_status=data.get('metadata', {}).get('status', 'unknown'),
                total_items=data.get('metadata', {}).get('total_items', 0)
            )

            # Upload to GCS
            logger.debug("Starting GCS upload phase")
            upload_success = self.upload_to_gcs(data)
            
            if upload_success:
                logger.info(
                    "DexScreener cycle completed successfully",
                    component="cycle",
                    operation="run_crawl_cycle",
                    status="success",
                    data_collected=len(data.get('latest_token_profiles', [])),
                    upload_success=True
                )
            else:
                logger.error(
                    "Failed to upload DexScreener data",
                    component="cycle",
                    operation="run_crawl_cycle",
                    status="upload_failed",
                    data_collected=len(data.get('latest_token_profiles', [])),
                    upload_success=False
                )

        except Exception as e:
            logger.error(
                "Error in DexScreener crawl cycle",
                error=str(e),
                traceback=traceback.format_exc(),
                component="cycle",
                operation="run_crawl_cycle",
                status="error"
            )

    async def run_continuous(self):
        """Run the continuous DexScreener crawler with comprehensive logging"""
        logger.info(
            "Starting Continuous DexScreener Crawler",
            component="continuous",
            operation="run_continuous",
            timestamp=datetime.now().isoformat(),
            interval_minutes=7
        )

        self.running = True
        cycle_count = 0
        total_start_time = time.time()

        try:
            while self.running:
                cycle_count += 1
                cycle_start_time = time.time()
                
                logger.info(
                    "Starting crawl cycle",
                    cycle_number=cycle_count,
                    total_runtime_seconds=time.time() - total_start_time,
                    component="continuous"
                )

                await self.run_crawl_cycle()
                cycle_duration = time.time() - cycle_start_time

                logger.info(
                    "Cycle completed",
                    cycle_number=cycle_count,
                    cycle_duration_seconds=cycle_duration,
                    total_runtime_seconds=time.time() - total_start_time,
                    component="continuous"
                )

                # Wait before next cycle (7 minutes between cycles)
                wait_time = 7 * 60  # 7 minutes
                logger.info(
                    "Sleeping before next cycle",
                    wait_time_seconds=wait_time,
                    wait_time_minutes=wait_time/60,
                    next_cycle_time=datetime.now() + timedelta(seconds=wait_time),
                    component="continuous"
                )
                await asyncio.sleep(wait_time)

        except KeyboardInterrupt:
            logger.info(
                "Received interrupt signal, stopping crawler",
                component="continuous",
                total_cycles=cycle_count,
                total_runtime_seconds=time.time() - total_start_time
            )
        except Exception as e:
            logger.error(
                "Error in continuous crawler",
                error=str(e),
                traceback=traceback.format_exc(),
                component="continuous",
                total_cycles=cycle_count,
                total_runtime_seconds=time.time() - total_start_time
            )
        finally:
            self.running = False
            logger.info(
                "Continuous DexScreener Crawler stopped",
                component="continuous",
                total_cycles=cycle_count,
                total_runtime_seconds=time.time() - total_start_time
            )


async def main():
    """Main entry point"""
    crawler = ContinuousDexScreenerCrawler()
    await crawler.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())
