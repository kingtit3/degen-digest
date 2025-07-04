#!/usr/bin/env python3
"""
Merge Local Twitter Crawling Data with Google Cloud Storage
Uploads local Twitter data files to GCS and creates a consolidated dataset
"""

import json
import logging
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Google Cloud Storage imports
try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print(
        "Warning: Google Cloud Storage not available. Install with: pip install google-cloud-storage"
    )

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataMerger:
    def __init__(
        self,
        local_output_dir: str = "output",
        gcs_bucket: str = "degen-digest-data",
        project_id: str = "lucky-union-463615-t3",
    ):
        self.local_output_dir = Path(local_output_dir)
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

    def get_local_twitter_files(self) -> list[Path]:
        """Get all local Twitter data files"""
        pattern = "twitter_playwright_enhanced_*.json"
        files = list(self.local_output_dir.glob(pattern))
        files.sort()  # Sort by filename (which includes timestamp)
        logger.info(f"Found {len(files)} local Twitter data files")
        return files

    def load_twitter_data(self, file_path: Path) -> dict[str, Any]:
        """Load Twitter data from a JSON file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            logger.info(
                f"Loaded {len(data.get('tweets', []))} tweets from {file_path.name}"
            )
            return data
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return {"tweets": []}

    def upload_to_gcs(self, local_file: Path) -> bool:
        """Upload a local file to Google Cloud Storage"""
        if not self.gcs_bucket:
            logger.warning("GCS not available, skipping upload")
            return False

        try:
            blob_name = f"twitter_data/{local_file.name}"
            blob = self.gcs_bucket.blob(blob_name)

            # Upload the file
            blob.upload_from_filename(str(local_file))
            logger.info(f"Uploaded {local_file.name} to GCS as {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Error uploading {local_file.name} to GCS: {e}")
            return False

    def create_consolidated_dataset(
        self, all_tweets: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create a consolidated dataset from all tweets"""
        consolidated = {
            "metadata": {
                "total_tweets": len(all_tweets),
                "consolidated_at": datetime.now(UTC).isoformat(),
                "source_files": len(self.get_local_twitter_files()),
                "data_sources": ["twitter_playwright_enhanced"],
            },
            "tweets": all_tweets,
        }
        return consolidated

    def save_consolidated_data(
        self,
        consolidated_data: dict[str, Any],
        filename: str = "twitter_consolidated.json",
    ):
        """Save consolidated data locally and to GCS"""
        # Save locally
        local_path = self.local_output_dir / filename
        try:
            with open(local_path, "w", encoding="utf-8") as f:
                json.dump(consolidated_data, f, indent=2, default=str)
            logger.info(f"Saved consolidated data locally: {local_path}")
        except Exception as e:
            logger.error(f"Error saving consolidated data locally: {e}")

        # Upload to GCS
        if self.gcs_bucket:
            try:
                blob_name = f"consolidated/{filename}"
                blob = self.gcs_bucket.blob(blob_name)
                blob.upload_from_filename(str(local_path))
                logger.info(f"Uploaded consolidated data to GCS: {blob_name}")
            except Exception as e:
                logger.error(f"Error uploading consolidated data to GCS: {e}")

    def merge_data(self) -> bool:
        """Main function to merge local and cloud data"""
        logger.info("🚀 Starting data merge process...")

        # Get local files
        local_files = self.get_local_twitter_files()
        if not local_files:
            logger.warning("No local Twitter data files found")
            return False

        all_tweets = []
        uploaded_count = 0

        # Process each local file
        for local_file in local_files:
            logger.info(f"Processing {local_file.name}...")

            # Load data
            data = self.load_twitter_data(local_file)
            tweets = data.get("tweets", [])
            all_tweets.extend(tweets)

            # Upload to GCS
            if self.upload_to_gcs(local_file):
                uploaded_count += 1

        logger.info(f"📊 Total tweets collected: {len(all_tweets)}")
        logger.info(f"📤 Files uploaded to GCS: {uploaded_count}/{len(local_files)}")

        # Create consolidated dataset
        if all_tweets:
            consolidated_data = self.create_consolidated_dataset(all_tweets)
            self.save_consolidated_data(consolidated_data)

            # Also create a latest version
            latest_data = {
                "metadata": {
                    "total_tweets": len(all_tweets),
                    "last_updated": datetime.now(UTC).isoformat(),
                    "source": "merged_local_cloud_data",
                },
                "tweets": all_tweets[-50:],  # Keep last 50 tweets for latest
            }
            self.save_consolidated_data(latest_data, "twitter_latest.json")

        logger.info("✅ Data merge completed successfully!")
        return True


def main():
    """Main function"""
    merger = DataMerger()
    success = merger.merge_data()

    if success:
        print("🎉 Data merge completed successfully!")
        print("📁 Check the output directory for consolidated files")
        print("☁️ Check GCS bucket for uploaded files")
    else:
        print("❌ Data merge failed")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
