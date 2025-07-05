#!/usr/bin/env python3
"""
DexScreener Cloud Task Handler
Deployed as Cloud Function or Cloud Run service
"""
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Add current directory to path
sys.path.append(".")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def crawl_dexscreener() -> dict[str, Any]:
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


def upload_to_gcs(data: dict[str, Any]) -> bool:
    """Upload data to Google Cloud Storage"""
    try:
        from google.cloud import storage

        bucket_name = "degen-digest-data"
        project_id = "lucky-union-463615-t3"

        client = storage.Client(project=project_id)
        bucket = client.bucket(bucket_name)

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


def dexscreener_task_handler(request):
    """Cloud Function handler for DexScreener task"""
    try:
        logger.info("🚀 Starting DexScreener Cloud Task...")

        # Crawl DexScreener data
        data = crawl_dexscreener()

        # Upload to GCS
        if upload_to_gcs(data):
            logger.info("✅ DexScreener Cloud Task completed successfully")
            return {
                "status": "success",
                "message": "DexScreener crawl completed",
                "data_count": len(data.get("latest_token_profiles", [])),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            logger.error("❌ Failed to upload DexScreener data")
            return {
                "status": "error",
                "message": "Failed to upload data",
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"❌ DexScreener Cloud Task failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# For Cloud Run compatibility
def dexscreener_cloud_run(request):
    """Cloud Run handler for DexScreener task"""
    return dexscreener_task_handler(request)


# Flask app for Cloud Run
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def handle_request():
    """Handle HTTP requests for Cloud Run"""
    if request.method == "GET":
        return jsonify({"status": "healthy", "service": "dexscreener-crawler"})
    elif request.method == "POST":
        result = dexscreener_task_handler(request)
        return jsonify(result)


if __name__ == "__main__":
    # For local testing
    if os.getenv("PORT"):
        # Cloud Run environment
        port = int(os.getenv("PORT", 8080))
        app.run(host="0.0.0.0", port=port)
    else:
        # Local testing
        result = dexscreener_task_handler(None)
        print(json.dumps(result, indent=2))
