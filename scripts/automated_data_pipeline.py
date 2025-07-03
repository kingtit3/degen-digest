#!/usr/bin/env python3
"""
Automated Data Pipeline for FarmChecker.xyz
Runs all scrapers with Twitter limited to once every 3 hours
"""

import json
import sqlite3
import subprocess
import sys
import time
from datetime import UTC, datetime, timezone
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.advanced_logging import get_logger

logger = get_logger(__name__)


class AutomatedDataPipeline:
    """Automated pipeline that runs all scrapers with smart scheduling"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.last_twitter_run_file = (
            self.project_root / "output" / "last_twitter_run.txt"
        )
        self.twitter_interval_hours = 3

        # Ensure output directory exists
        (self.project_root / "output").mkdir(exist_ok=True)

    def should_run_twitter(self) -> bool:
        """Check if Twitter should be scraped (once every 3 hours)"""
        if not self.last_twitter_run_file.exists():
            return True

        try:
            with open(self.last_twitter_run_file) as f:
                last_run_str = f.read().strip()
                last_run = datetime.fromisoformat(last_run_str)

            time_since_last = datetime.now(UTC) - last_run
            return time_since_last.total_seconds() >= (
                self.twitter_interval_hours * 3600
            )

        except Exception as e:
            logger.warning(f"Error reading last Twitter run time: {e}")
            return True

    def mark_twitter_run(self):
        """Mark that Twitter was just scraped"""
        try:
            with open(self.last_twitter_run_file, "w") as f:
                f.write(datetime.now(UTC).isoformat())
        except Exception as e:
            logger.error(f"Error marking Twitter run: {e}")

    def run_scraper(self, script_name: str, description: str) -> bool:
        """Run a scraper script and return success status"""
        logger.info(f"🔄 Running {description}...")

        try:
            script_path = self.project_root / script_name
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info(f"✅ {description} completed successfully")
                return True
            else:
                logger.error(f"❌ {description} failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"⏰ {description} timed out after 5 minutes")
            return False
        except Exception as e:
            logger.error(f"❌ {description} error: {e}")
            return False

    def run_continuous_pipeline(self):
        """Run the continuous data pipeline"""
        logger.info("🚀 Starting Automated Data Pipeline for FarmChecker.xyz")
        logger.info("=" * 60)

        while True:
            try:
                current_time = datetime.now(UTC)
                logger.info(
                    f"📅 Pipeline run at: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                )

                # Always run these scrapers (they're fast and have good rate limits)
                scrapers_to_run = [
                    ("scrapers/reddit_rss.py", "Reddit RSS Scraper"),
                    ("scrapers/newsapi_headlines.py", "News API Headlines"),
                    ("scrapers/coingecko_gainers.py", "CoinGecko Gainers"),
                ]

                # Add Twitter only if it's time
                if self.should_run_twitter():
                    scrapers_to_run.append(
                        (
                            "scrapers/enhanced_twitter_scraper.py",
                            "Enhanced Twitter Scraper",
                        )
                    )
                    scrapers_to_run.append(
                        ("scrapers/twitter_apify.py", "Twitter Apify Scraper")
                    )
                    self.mark_twitter_run()
                    logger.info("🐦 Twitter scraping enabled for this run")
                else:
                    logger.info("⏳ Twitter scraping skipped (runs every 3 hours)")

                # Run all enabled scrapers
                successful_scrapes = 0
                for script, description in scrapers_to_run:
                    if self.run_scraper(script, description):
                        successful_scrapes += 1
                    time.sleep(2)  # Small delay between scrapers

                # Run data processing
                logger.info("🔄 Processing collected data...")

                # Deduplicate data
                if self.run_scraper("run_deduplication.py", "Data Deduplication"):
                    logger.info("✅ Data deduplication completed")

                # Generate digest
                if self.run_scraper("fetch_todays_digest.py", "Generate Daily Digest"):
                    logger.info("✅ Daily digest generated")

                # Run intelligent analysis
                if self.run_scraper(
                    "run_intelligent_analysis.py", "Intelligent Analysis"
                ):
                    logger.info("✅ Intelligent analysis completed")

                # Update database
                if self.run_scraper("recreate_db.py", "Database Update"):
                    logger.info("✅ Database updated")

                # Check data quality
                self.check_data_quality()

                logger.info(
                    f"✅ Pipeline run completed. {successful_scrapes}/{len(scrapers_to_run)} scrapers successful"
                )
                logger.info("=" * 60)

                # Wait 30 minutes before next run
                logger.info("⏳ Waiting 30 minutes before next pipeline run...")
                time.sleep(1800)  # 30 minutes

            except KeyboardInterrupt:
                logger.info("🛑 Pipeline stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Pipeline error: {e}")
                logger.info("⏳ Waiting 5 minutes before retry...")
                time.sleep(300)  # 5 minutes

    def check_data_quality(self):
        """Check the quality and volume of collected data"""
        try:
            # Check consolidated data
            consolidated_file = self.project_root / "output" / "consolidated_data.json"
            if consolidated_file.exists():
                with open(consolidated_file) as f:
                    data = json.load(f)

                total_items = 0
                for source in ["tweets", "reddit_posts", "news"]:
                    if source in data:
                        count = len(data[source])
                        total_items += count
                        logger.info(f"📊 {source}: {count} items")

                logger.info(f"📈 Total items collected: {total_items}")

                # Alert if data is too low
                if total_items < 50:
                    logger.warning("⚠️ Low data volume detected!")

            # Check database
            db_file = self.project_root / "output" / "degen_digest.db"
            if db_file.exists():
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()

                # Count recent items
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM tweets
                    WHERE created_at >= datetime('now', '-1 hour')
                """
                )
                recent_tweets = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT COUNT(*) FROM reddit_posts
                    WHERE created_at >= datetime('now', '-1 hour')
                """
                )
                recent_reddit = cursor.fetchone()[0]

                logger.info(
                    f"🗄️ Recent items in DB: {recent_tweets} tweets, {recent_reddit} reddit posts"
                )
                conn.close()

        except Exception as e:
            logger.error(f"Error checking data quality: {e}")


def main():
    """Main function"""
    pipeline = AutomatedDataPipeline()

    print("🚀 Automated Data Pipeline for FarmChecker.xyz")
    print("=" * 60)
    print("📋 Configuration:")
    print(f"   • Twitter scraping: Every {pipeline.twitter_interval_hours} hours")
    print("   • Other scrapers: Every 30 minutes")
    print("   • Data processing: After each scrape run")
    print("   • Pipeline runs continuously")
    print("=" * 60)

    try:
        pipeline.run_continuous_pipeline()
    except KeyboardInterrupt:
        print("\n🛑 Pipeline stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    main()
