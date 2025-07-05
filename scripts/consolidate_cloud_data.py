#!/usr/bin/env python3
"""
Consolidate Cloud Data for Dashboard
Processes raw data from GCS and creates consolidated files for the dashboard
"""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

# Google Cloud Storage imports
try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("Warning: Google Cloud Storage not available")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudDataConsolidator:
    def __init__(
        self,
        gcs_bucket: str = "degen-digest-data",
        project_id: str = "lucky-union-463615-t3",
    ):
        self.gcs_bucket_name = gcs_bucket
        self.project_id = project_id
        self.gcs_client = None
        self.gcs_bucket = None

        # Initialize Google Cloud Storage
        if GCS_AVAILABLE:
            try:
                self.gcs_client = storage.Client(project=project_id)
                self.gcs_bucket = self.gcs_client.bucket(gcs_bucket)
                logger.info(f"GCS initialized: {gcs_bucket} in project: {project_id}")
            except Exception as e:
                logger.error(f"Error accessing GCS bucket {gcs_bucket}: {e}")
                self.gcs_bucket = None
        else:
            logger.warning("Google Cloud Storage not available")

    def get_latest_raw_data(self, source: str) -> dict[str, Any]:
        """Get the latest raw data for a source from GCS"""
        if not self.gcs_bucket:
            return {}

        try:
            # For Twitter, try the enhanced crawler format first
            if source == "twitter":
                latest_path = f"{source}_data/twitter_playwright_enhanced_latest.json"
                blob = self.gcs_bucket.blob(latest_path)

                if blob.exists():
                    content = blob.download_as_text()
                    data = json.loads(content)
                    logger.info(
                        f"Loaded latest {source} data: {len(data.get('tweets', data.get('posts', data.get('articles', data.get('messages', [])))))} items"
                    )
                    return data
                else:
                    # Fallback to regular format
                    latest_path = f"{source}_data/{source}_latest.json"
                    blob = self.gcs_bucket.blob(latest_path)
            else:
                # Try to get the latest file
                latest_path = f"{source}_data/{source}_latest.json"
                blob = self.gcs_bucket.blob(latest_path)

            if blob.exists():
                content = blob.download_as_text()
                data = json.loads(content)
                # Count items based on source type
                if source == "twitter":
                    count = len(data.get("tweets", []))
                elif source == "reddit":
                    count = len(data.get("posts", []))
                elif source == "news":
                    count = len(data.get("articles", []))
                elif source == "telegram":
                    count = len(data.get("messages", []))
                elif source == "crypto":
                    count = len(data.get("gainers", []))
                elif source == "dexscreener":
                    count = len(data.get("latest_token_profiles", []))
                elif source == "dexpaprika":
                    count = len(data.get("token_data", []))
                else:
                    count = len(
                        data.get(
                            "tweets",
                            data.get(
                                "posts", data.get("articles", data.get("messages", []))
                            ),
                        )
                    )
                logger.info(f"Loaded latest {source} data: {count} items")
                return data
            else:
                logger.warning(f"No latest {source} data found in GCS")
                return {}
        except Exception as e:
            logger.error(f"Error loading {source} data from GCS: {e}")
            return {}

    def consolidate_twitter_data(self) -> dict[str, Any]:
        """Consolidate Twitter data"""
        raw_data = self.get_latest_raw_data("twitter")

        if not raw_data:
            return {
                "metadata": {
                    "source": "twitter",
                    "consolidated_at": datetime.now(UTC).isoformat(),
                    "status": "no_data",
                },
                "tweets": [],
            }

        tweets = raw_data.get("tweets", [])

        consolidated = {
            "metadata": {
                "consolidated_at": datetime.now(UTC).isoformat(),
                "total_tweets": len(tweets),
                "source_files": 1,
                "unique_tweets": len(tweets),
            },
            "tweets": tweets,
        }

        return consolidated

    def consolidate_reddit_data(self) -> dict[str, Any]:
        """Consolidate Reddit data"""
        raw_data = self.get_latest_raw_data("reddit")

        if not raw_data:
            return {
                "metadata": {
                    "source": "reddit",
                    "consolidated_at": datetime.now(UTC).isoformat(),
                    "status": "no_data",
                },
                "posts": [],
            }

        posts = raw_data.get("posts", [])

        consolidated = {
            "metadata": {
                "consolidated_at": datetime.now(UTC).isoformat(),
                "total_posts": len(posts),
                "source_files": 1,
                "unique_posts": len(posts),
            },
            "posts": posts,
        }

        return consolidated

    def consolidate_news_data(self) -> dict[str, Any]:
        """Consolidate News data"""
        raw_data = self.get_latest_raw_data("news")

        if not raw_data:
            return {
                "metadata": {
                    "source": "news",
                    "consolidated_at": datetime.now(UTC).isoformat(),
                    "status": "no_data",
                },
                "articles": [],
            }

        articles = raw_data.get("articles", [])

        consolidated = {
            "metadata": {
                "consolidated_at": datetime.now(UTC).isoformat(),
                "total_articles": len(articles),
                "source_files": 1,
                "unique_articles": len(articles),
            },
            "articles": articles,
        }

        return consolidated

    def consolidate_telegram_data(self) -> dict[str, Any]:
        """Consolidate Telegram data"""
        raw_data = self.get_latest_raw_data("telegram")

        if not raw_data:
            return {
                "metadata": {
                    "source": "telegram",
                    "consolidated_at": datetime.now(UTC).isoformat(),
                    "status": "no_data",
                },
                "messages": [],
            }

        messages = raw_data.get("messages", [])

        consolidated = {
            "metadata": {
                "consolidated_at": datetime.now(UTC).isoformat(),
                "total_messages": len(messages),
                "source_files": 1,
                "unique_messages": len(messages),
            },
            "messages": messages,
        }

        return consolidated

    def consolidate_crypto_data(self) -> dict[str, Any]:
        """Consolidate Crypto data"""
        raw_data = self.get_latest_raw_data("crypto")

        if not raw_data:
            return {
                "metadata": {
                    "source": "crypto",
                    "consolidated_at": datetime.now(UTC).isoformat(),
                    "status": "no_data",
                },
                "gainers": [],
            }

        gainers = raw_data.get("gainers", [])

        consolidated = {
            "metadata": {
                "consolidated_at": datetime.now(UTC).isoformat(),
                "total_gainers": len(gainers),
                "source_files": 1,
                "unique_gainers": len(gainers),
            },
            "gainers": gainers,
        }

        return consolidated

    def consolidate_dexscreener_data(self) -> dict[str, Any]:
        """Consolidate DEX Screener data"""
        raw_data = self.get_latest_raw_data("dexscreener")
        if not raw_data:
            return {
                "metadata": {
                    "source": "dexscreener",
                    "consolidated_at": datetime.now(UTC).isoformat(),
                    "status": "no_data",
                },
                "latest_token_profiles": [],
                "latest_boosted_tokens": [],
                "top_boosted_tokens": [],
                "token_pairs": [],
                "tokens_by_address": [],
                "pair_by_id": {},
                "search_pairs": {},
            }
        consolidated = {
            "metadata": {
                "consolidated_at": datetime.now(UTC).isoformat(),
                "source_files": 1,
                "status": "success",
            },
            "latest_token_profiles": raw_data.get("latest_token_profiles", []),
            "latest_boosted_tokens": raw_data.get("latest_boosted_tokens", []),
            "top_boosted_tokens": raw_data.get("top_boosted_tokens", []),
            "token_pairs": raw_data.get("token_pairs", []),
            "tokens_by_address": raw_data.get("tokens_by_address", []),
            "pair_by_id": raw_data.get("pair_by_id", {}),
            "search_pairs": raw_data.get("search_pairs", {}),
        }
        return consolidated

    def consolidate_dexpaprika_data(self) -> dict[str, Any]:
        """Consolidate DexPaprika data"""
        raw_data = self.get_latest_raw_data("dexpaprika")
        if not raw_data:
            return {
                "metadata": {
                    "source": "dexpaprika",
                    "consolidated_at": datetime.now(UTC).isoformat(),
                    "status": "no_data",
                },
                "networks": [],
                "token_data": [],
                "summary": {},
            }
        consolidated = {
            "metadata": {
                "consolidated_at": datetime.now(UTC).isoformat(),
                "source_files": 1,
                "status": "success",
            },
            "networks": raw_data.get("networks", []),
            "token_data": raw_data.get("token_data", []),
            "summary": raw_data.get("summary", {}),
        }
        return consolidated

    def save_consolidated_data(self, data: dict[str, Any], source: str):
        """Save consolidated data to GCS"""
        if not self.gcs_bucket:
            logger.warning("GCS not available, skipping save")
            return False

        try:
            # Save consolidated data
            consolidated_path = f"consolidated/{source}_consolidated.json"
            blob = self.gcs_bucket.blob(consolidated_path)
            blob.upload_from_string(
                json.dumps(data, indent=2, ensure_ascii=False),
                content_type="application/json",
            )
            logger.info(
                f"✅ Saved {source} consolidated data to GCS: {consolidated_path}"
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error saving {source} consolidated data: {e}")
            return False

    def run_consolidation(self):
        """Run the complete consolidation process"""
        logger.info("🚀 Starting cloud data consolidation...")

        sources = [
            "twitter",
            "reddit",
            "news",
            "telegram",
            "crypto",
            "dexscreener",
            "dexpaprika",
        ]
        consolidation_functions = {
            "twitter": self.consolidate_twitter_data,
            "reddit": self.consolidate_reddit_data,
            "news": self.consolidate_news_data,
            "telegram": self.consolidate_telegram_data,
            "crypto": self.consolidate_crypto_data,
            "dexscreener": self.consolidate_dexscreener_data,
            "dexpaprika": self.consolidate_dexpaprika_data,
        }

        success_count = 0
        total_count = len(sources)

        for source in sources:
            logger.info(f"🔄 Consolidating {source} data...")

            try:
                # Consolidate data
                consolidated_data = consolidation_functions[source]()

                # Save to GCS
                if self.save_consolidated_data(consolidated_data, source):
                    success_count += 1
                    logger.info(f"✅ {source} consolidation completed")
                else:
                    logger.error(f"❌ {source} consolidation failed")

            except Exception as e:
                logger.error(f"❌ Error consolidating {source} data: {e}")

        logger.info(
            f"📊 Consolidation complete: {success_count}/{total_count} sources processed"
        )
        return success_count == total_count


def main():
    """Main function"""
    consolidator = CloudDataConsolidator()
    success = consolidator.run_consolidation()

    if success:
        print("🎉 All data consolidated successfully!")
        print("📊 Dashboard should now have access to fresh consolidated data")
    else:
        print("⚠️ Some data consolidation failed")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
