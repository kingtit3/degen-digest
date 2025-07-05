#!/usr/bin/env python3
"""
Data Aggregator Service
Consolidates data from all crawler services and generates digests
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

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


class DataAggregator:
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

    def download_latest_data(self) -> dict[str, Any]:
        """Download latest data from all crawler services"""
        client, bucket = self.get_gcs_client()
        if not bucket:
            return {}

        consolidated_data = {
            "twitter": {"posts": []},
            "reddit": {"posts": []},
            "news": {"articles": []},
            "crypto": {"gainers": []},
            "metadata": {
                "consolidated_at": datetime.now(UTC).isoformat(),
                "sources": [],
            },
        }

        # Download latest data from each source
        sources = ["twitter", "reddit", "news", "crypto"]

        for source in sources:
            try:
                logger.info(f"🔄 Downloading latest {source} data...")

                # Try to get latest data
                latest_blob = bucket.blob(f"{source}_data/{source}_latest.json")

                if latest_blob.exists():
                    content = latest_blob.download_as_text()
                    data = json.loads(content)

                    # Extract the main data array
                    if source == "twitter" and "posts" in data:
                        consolidated_data[source]["posts"] = data["posts"]
                    elif source == "reddit" and "posts" in data:
                        consolidated_data[source]["posts"] = data["posts"]
                    elif source == "news" and "articles" in data:
                        consolidated_data[source]["articles"] = data["articles"]
                    elif source == "crypto" and "gainers" in data:
                        consolidated_data[source]["gainers"] = data["gainers"]

                    consolidated_data["metadata"]["sources"].append(source)
                    logger.info(
                        f"  ✅ {source}: {len(data.get('posts', data.get('articles', data.get('gainers', []))))} items"
                    )
                else:
                    logger.warning(f"  ⚠️ No latest data found for {source}")

            except Exception as e:
                logger.error(f"  ❌ Failed to download {source} data: {e}")

        return consolidated_data

    def upload_consolidated_data(self, data: dict[str, Any]):
        """Upload consolidated data to GCS"""
        client, bucket = self.get_gcs_client()
        if not bucket:
            return False

        try:
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"consolidated_data/consolidated_{timestamp}.json"

            # Upload data
            blob = bucket.blob(filename)
            blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            # Also upload as latest
            latest_filename = "consolidated_data/consolidated_latest.json"
            latest_blob = bucket.blob(latest_filename)
            latest_blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )

            logger.info(f"✅ Uploaded consolidated data to GCS: {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload consolidated data to GCS: {e}")
            return False

    def generate_digest_summary(self, data: dict[str, Any]) -> str:
        """Generate a simple digest summary"""
        summary = []
        summary.append("# Degen Digest - Data Summary")
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        summary.append("")

        # Twitter summary
        twitter_count = len(data.get("twitter", {}).get("posts", []))
        summary.append(f"## Twitter: {twitter_count} posts")
        if twitter_count > 0:
            for i, post in enumerate(data["twitter"]["posts"][:3]):  # Top 3
                summary.append(f"{i+1}. {post.get('text', '')[:100]}...")
        summary.append("")

        # Reddit summary
        reddit_count = len(data.get("reddit", {}).get("posts", []))
        summary.append(f"## Reddit: {reddit_count} posts")
        if reddit_count > 0:
            for i, post in enumerate(data["reddit"]["posts"][:3]):  # Top 3
                summary.append(f"{i+1}. {post.get('title', '')[:100]}...")
        summary.append("")

        # News summary
        news_count = len(data.get("news", {}).get("articles", []))
        summary.append(f"## News: {news_count} articles")
        if news_count > 0:
            for i, article in enumerate(data["news"]["articles"][:3]):  # Top 3
                summary.append(f"{i+1}. {article.get('title', '')[:100]}...")
        summary.append("")

        # Crypto summary
        crypto_count = len(data.get("crypto", {}).get("gainers", []))
        summary.append(f"## Crypto: {crypto_count} trending items")
        if crypto_count > 0:
            for i, item in enumerate(data["crypto"]["gainers"][:5]):  # Top 5
                name = item.get("name", item.get("symbol", "Unknown"))
                change = item.get(
                    "price_change_percentage_24h", item.get("price_change_24h", 0)
                )
                summary.append(f"{i+1}. {name}: {change:.2f}%")

        return "\n".join(summary)

    def upload_digest(self, digest_content: str):
        """Upload digest to GCS"""
        client, bucket = self.get_gcs_client()
        if not bucket:
            return False

        try:
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"digests/digest_{timestamp}.md"

            # Upload digest
            blob = bucket.blob(filename)
            blob.upload_from_string(
                digest_content,
                content_type="text/markdown",
            )

            # Also upload as latest
            latest_filename = "digests/digest_latest.md"
            latest_blob = bucket.blob(latest_filename)
            latest_blob.upload_from_string(
                digest_content,
                content_type="text/markdown",
            )

            logger.info(f"✅ Uploaded digest to GCS: {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload digest to GCS: {e}")
            return False

    async def run_aggregation(self):
        """Run the data aggregation process"""
        logger.info("🔄 Starting data aggregation...")

        # Download latest data from all sources
        consolidated_data = self.download_latest_data()

        # Upload consolidated data
        if self.upload_consolidated_data(consolidated_data):
            logger.info("✅ Consolidated data uploaded successfully")
        else:
            logger.error("❌ Failed to upload consolidated data")

        # Generate and upload digest
        digest_content = self.generate_digest_summary(consolidated_data)
        if self.upload_digest(digest_content):
            logger.info("✅ Digest generated and uploaded successfully")
        else:
            logger.error("❌ Failed to upload digest")

        # Print summary
        total_items = (
            len(consolidated_data.get("twitter", {}).get("posts", []))
            + len(consolidated_data.get("reddit", {}).get("posts", []))
            + len(consolidated_data.get("news", {}).get("articles", []))
            + len(consolidated_data.get("crypto", {}).get("gainers", []))
        )

        logger.info("📊 Aggregation Summary:")
        logger.info(f"  - Total items: {total_items}")
        logger.info(
            f"  - Sources: {', '.join(consolidated_data['metadata']['sources'])}"
        )

        return consolidated_data


async def main():
    """Main function for data aggregator"""
    aggregator = DataAggregator()

    # Run aggregation
    result = await aggregator.run_aggregation()

    return result


if __name__ == "__main__":
    asyncio.run(main())
