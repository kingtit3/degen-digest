#!/usr/bin/env python3
"""
Data Merging Script for Degen Digest
Merges local and Google Cloud data to ensure consistency and completeness.
"""

import json
import logging
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataMerger:
    def __init__(self, local_root: str = ".", cloud_bucket: str = "degen-digest-data"):
        self.local_root = Path(local_root)
        self.cloud_bucket = cloud_bucket
        self.output_dir = self.local_root / "output"
        self.db_path = self.output_dir / "degen_digest.db"

    def merge_all_data(self):
        """Main method to merge all data sources"""
        logger.info("Starting data merge process...")

        # 1. Database sync
        self.sync_database()

        # 2. File sync
        self.sync_files()

        # 3. Data consolidation
        self.consolidate_data()

        # 4. Enhanced pipeline data
        self.merge_enhanced_pipeline()

        # 5. Generate merge report
        self.generate_merge_report()

        logger.info("Data merge completed!")

    def sync_database(self):
        """Sync local database with cloud database if available"""
        logger.info("Syncing database...")

        # Check if local database exists
        if not self.db_path.exists():
            logger.warning("Local database not found, creating new one")
            self.create_empty_database()
            return

        # For now, we'll work with local database
        # In production, you'd download cloud database and merge
        logger.info("Using local database")

        # Backup current database
        backup_path = self.db_path.with_suffix(
            f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"Database backed up to {backup_path}")

    def create_empty_database(self):
        """Create empty database with proper schema"""
        import sys

        sys.path.append(str(self.local_root))

        from storage.db import SQLModel, engine

        SQLModel.metadata.create_all(engine)
        logger.info("Created new database with schema")

    def sync_files(self):
        """Sync local files with cloud storage"""
        logger.info("Syncing files...")

        # List of important files to sync
        important_files = [
            "twitter_raw.json",
            "reddit_raw.json",
            "telegram_raw.json",
            "newsapi_raw.json",
            "coingecko_raw.json",
            "enhanced_twitter_data.json",
            "health_metrics.json",
            "health_alerts.json",
        ]

        for filename in important_files:
            file_path = self.output_dir / filename
            if file_path.exists():
                logger.info(f"Found local file: {filename}")
                # In production, you'd upload to cloud here
            else:
                logger.warning(f"Missing local file: {filename}")

    def consolidate_data(self):
        """Consolidate data from multiple sources into unified format"""
        logger.info("Consolidating data...")

        consolidated_data = {
            "tweets": [],
            "reddit_posts": [],
            "telegram_messages": [],
            "news_articles": [],
            "crypto_data": [],
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "sources": [],
                "total_items": 0,
            },
        }

        # Load and consolidate Twitter data
        twitter_file = self.output_dir / "twitter_raw.json"
        if twitter_file.exists():
            try:
                with open(twitter_file) as f:
                    twitter_data = json.load(f)
                consolidated_data["tweets"] = twitter_data
                consolidated_data["metadata"]["sources"].append("twitter")
                consolidated_data["metadata"]["total_items"] += len(twitter_data)
                logger.info(f"Loaded {len(twitter_data)} tweets")
            except Exception as e:
                logger.error(f"Error loading Twitter data: {e}")

        # Load and consolidate Reddit data
        reddit_file = self.output_dir / "reddit_raw.json"
        if reddit_file.exists():
            try:
                with open(reddit_file) as f:
                    reddit_data = json.load(f)
                consolidated_data["reddit_posts"] = reddit_data
                consolidated_data["metadata"]["sources"].append("reddit")
                consolidated_data["metadata"]["total_items"] += len(reddit_data)
                logger.info(f"Loaded {len(reddit_data)} Reddit posts")
            except Exception as e:
                logger.error(f"Error loading Reddit data: {e}")

        # Load and consolidate Telegram data
        telegram_file = self.output_dir / "telegram_raw.json"
        if telegram_file.exists():
            try:
                with open(telegram_file) as f:
                    telegram_data = json.load(f)
                consolidated_data["telegram_messages"] = telegram_data
                consolidated_data["metadata"]["sources"].append("telegram")
                consolidated_data["metadata"]["total_items"] += len(telegram_data)
                logger.info(f"Loaded {len(telegram_data)} Telegram messages")
            except Exception as e:
                logger.error(f"Error loading Telegram data: {e}")

        # Load and consolidate News data
        news_file = self.output_dir / "newsapi_raw.json"
        if news_file.exists():
            try:
                with open(news_file) as f:
                    news_data = json.load(f)
                consolidated_data["news_articles"] = news_data
                consolidated_data["metadata"]["sources"].append("news")
                consolidated_data["metadata"]["total_items"] += len(news_data)
                logger.info(f"Loaded {len(news_data)} news articles")
            except Exception as e:
                logger.error(f"Error loading news data: {e}")

        # Load and consolidate Crypto data
        crypto_file = self.output_dir / "coingecko_raw.json"
        if crypto_file.exists():
            try:
                with open(crypto_file) as f:
                    crypto_data = json.load(f)
                consolidated_data["crypto_data"] = crypto_data
                consolidated_data["metadata"]["sources"].append("crypto")
                consolidated_data["metadata"]["total_items"] += len(crypto_data)
                logger.info(f"Loaded {len(crypto_data)} crypto data points")
            except Exception as e:
                logger.error(f"Error loading crypto data: {e}")

        # Save consolidated data
        consolidated_file = self.output_dir / "consolidated_data.json"
        with open(consolidated_file, "w") as f:
            json.dump(consolidated_data, f, indent=2, default=str)

        logger.info(f"Consolidated data saved to {consolidated_file}")
        logger.info(f"Total items: {consolidated_data['metadata']['total_items']}")

    def merge_enhanced_pipeline(self):
        """Merge enhanced pipeline data"""
        logger.info("Merging enhanced pipeline data...")

        pipeline_dir = self.output_dir / "enhanced_pipeline"
        if not pipeline_dir.exists():
            logger.warning("Enhanced pipeline directory not found")
            return

        # Load viral predictions
        viral_file = pipeline_dir / "viral_predictions.json"
        if viral_file.exists():
            try:
                with open(viral_file) as f:
                    viral_data = json.load(f)
                logger.info(f"Loaded {len(viral_data)} viral predictions")

                # Merge with main consolidated data
                consolidated_file = self.output_dir / "consolidated_data.json"
                if consolidated_file.exists():
                    with open(consolidated_file) as f:
                        consolidated = json.load(f)

                    consolidated["viral_predictions"] = viral_data
                    consolidated["metadata"]["sources"].append("viral_predictions")

                    with open(consolidated_file, "w") as f:
                        json.dump(consolidated, f, indent=2, default=str)

                    logger.info("Viral predictions merged into consolidated data")
            except Exception as e:
                logger.error(f"Error loading viral predictions: {e}")

        # Load processed data
        processed_file = pipeline_dir / "processed_data.json"
        if processed_file.exists():
            try:
                with open(processed_file) as f:
                    processed_data = json.load(f)
                logger.info(f"Loaded {len(processed_data)} processed items")

                # Save as separate file for dashboard access
                dashboard_file = self.output_dir / "dashboard_processed_data.json"
                with open(dashboard_file, "w") as f:
                    json.dump(processed_data, f, indent=2, default=str)

                logger.info(f"Processed data saved for dashboard: {dashboard_file}")
            except Exception as e:
                logger.error(f"Error loading processed data: {e}")

    def generate_merge_report(self):
        """Generate a report of the merge operation"""
        logger.info("Generating merge report...")

        report = {
            "merge_timestamp": datetime.now().isoformat(),
            "local_data": {},
            "cloud_data": {},
            "merge_summary": {},
            "recommendations": [],
        }

        # Analyze local data
        if self.db_path.exists():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get table counts
            tables = ["Tweet", "RedditPost", "Digest", "LLMUsage", "TweetMetrics"]
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    report["local_data"][table] = count
                except Exception:
                    report["local_data"][table] = 0

            conn.close()

        # Analyze file sizes
        important_files = [
            "twitter_raw.json",
            "reddit_raw.json",
            "telegram_raw.json",
            "newsapi_raw.json",
            "coingecko_raw.json",
            "consolidated_data.json",
        ]

        for filename in important_files:
            file_path = self.output_dir / filename
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                report["local_data"][filename] = f"{size_mb:.2f} MB"
            else:
                report["local_data"][filename] = "Missing"

        # Generate recommendations
        if report["local_data"].get("Tweet", 0) < 100:
            report["recommendations"].append(
                "Low tweet count - consider running Twitter scraper"
            )

        if report["local_data"].get("RedditPost", 0) < 50:
            report["recommendations"].append(
                "Low Reddit post count - consider running Reddit scraper"
            )

        missing_files = [
            f for f, status in report["local_data"].items() if status == "Missing"
        ]
        if missing_files:
            report["recommendations"].append(
                f"Missing files: {', '.join(missing_files)}"
            )

        # Save report
        report_file = self.output_dir / "merge_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Merge report saved to {report_file}")

        # Print summary
        print("\n" + "=" * 50)
        print("DATA MERGE SUMMARY")
        print("=" * 50)
        print("Database Tables:")
        for table, count in report["local_data"].items():
            if isinstance(count, int):
                print(f"  {table}: {count} records")
        print("\nFiles:")
        for file, status in report["local_data"].items():
            if not isinstance(status, int):
                print(f"  {file}: {status}")
        print("\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")
        print("=" * 50)


def main():
    """Main function to run the data merger"""
    merger = DataMerger()
    merger.merge_all_data()


if __name__ == "__main__":
    main()
