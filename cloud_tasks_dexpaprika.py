#!/usr/bin/env python3
"""
DexPaprika Cloud Task Handler
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


def crawl_dexpaprika() -> dict[str, Any]:
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

        logger.info(f"✅ DexPaprika crawl completed: {len(data['token_data'])} tokens")
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


def dexpaprika_task_handler(request):
    """Cloud Function handler for DexPaprika task"""
    try:
        logger.info("🚀 Starting DexPaprika Cloud Task...")

        # Crawl DexPaprika data
        data = crawl_dexpaprika()

        # Upload to GCS
        if upload_to_gcs(data):
            logger.info("✅ DexPaprika Cloud Task completed successfully")
            return {
                "status": "success",
                "message": "DexPaprika crawl completed",
                "data_count": len(data.get("token_data", [])),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            logger.error("❌ Failed to upload DexPaprika data")
            return {
                "status": "error",
                "message": "Failed to upload data",
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"❌ DexPaprika Cloud Task failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# For Cloud Run compatibility
def dexpaprika_cloud_run(request):
    """Cloud Run handler for DexPaprika task"""
    return dexpaprika_task_handler(request)


# Flask app for Cloud Run
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def handle_request():
    """Handle HTTP requests for Cloud Run"""
    if request.method == "GET":
        return jsonify({"status": "healthy", "service": "dexpaprika-crawler"})
    elif request.method == "POST":
        result = dexpaprika_task_handler(request)
        return jsonify(result)


if __name__ == "__main__":
    # For local testing
    if os.getenv("PORT"):
        # Cloud Run environment
        port = int(os.getenv("PORT", 8080))
        app.run(host="0.0.0.0", port=port)
    else:
        # Local testing
        result = dexpaprika_task_handler(None)
        print(json.dumps(result, indent=2))
