#!/usr/bin/env python3
"""
Comprehensive Data Cleanup Script for Degen Digest
Handles deduplication, cache clearing, and data organization.
"""

import hashlib
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ComprehensiveDataCleanup:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.deduplicated_dir = self.output_dir / "deduplicated"
        self.backup_dir = self.output_dir / "backups"
        self.deduplicated_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)

    def clear_all_caches(self):
        """Clear all cache files and directories"""
        logger.info("🧹 Clearing all caches...")

        cache_locations = [
            Path.home() / ".streamlit" / "cache",
            Path("output/llm_cache.sqlite"),
            Path("output/.cache"),
            Path("dashboard/.cache"),
            Path(".cache"),
        ]

        cleared_count = 0
        for cache_location in cache_locations:
            if cache_location.exists():
                try:
                    if cache_location.is_file():
                        cache_location.unlink()
                    else:
                        shutil.rmtree(cache_location)
                    logger.info(f"✅ Cleared: {cache_location}")
                    cleared_count += 1
                except Exception as e:
                    logger.error(f"❌ Error clearing {cache_location}: {e}")

        # Clear __pycache__ directories
        pycache_dirs = list(Path(".").rglob("__pycache__"))
        for pycache in pycache_dirs:
            try:
                shutil.rmtree(pycache)
                logger.info(f"✅ Cleared __pycache__: {pycache}")
                cleared_count += 1
            except Exception as e:
                logger.error(f"❌ Error clearing {pycache}: {e}")

        logger.info(f"🎉 Cache clearing completed! Cleared {cleared_count} locations")
        return cleared_count

    def backup_original_data(self):
        """Create backup of original data files"""
        logger.info("💾 Creating backup of original data...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)

        files_to_backup = [
            "twitter_raw.json",
            "reddit_raw.json",
            "telegram_raw.json",
            "newsapi_raw.json",
            "consolidated_data.json",
            "coingecko_raw.json",
        ]

        backed_up_count = 0
        for filename in files_to_backup:
            src = self.output_dir / filename
            if src.exists():
                try:
                    shutil.copy2(src, backup_path / filename)
                    logger.info(f"✅ Backed up: {filename}")
                    backed_up_count += 1
                except Exception as e:
                    logger.error(f"❌ Error backing up {filename}: {e}")

        logger.info(f"💾 Backup created: {backup_path} ({backed_up_count} files)")
        return backup_path

    def generate_content_hash(self, item: dict[str, Any]) -> str:
        """Generate a hash for content-based deduplication"""
        text = ""

        # For tweets
        if item.get("source") == "twitter" or "full_text" in item:
            text = item.get("full_text", item.get("text", ""))
            text += str(item.get("userScreenName", ""))
            text += str(item.get("createdAt", ""))

        # For Reddit posts
        elif item.get("source") == "reddit" or "title" in item:
            text = item.get("title", "")
            text += str(item.get("author", ""))
            text += str(item.get("published", ""))

        # For Telegram messages
        elif item.get("source") == "telegram" or "message" in item:
            text = item.get("message", "")
            text += str(item.get("sender", ""))
            text += str(item.get("date", ""))

        # For news articles
        elif item.get("source") == "news" or "title" in item:
            text = item.get("title", "")
            text += str(item.get("author", ""))
            text += str(item.get("publishedAt", ""))

        # Normalize text
        text = text.lower().strip()
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def deduplicate_data_source(
        self, filename: str, source_name: str
    ) -> dict[str, Any]:
        """Deduplicate a specific data source"""
        logger.info(f"🔍 Deduplicating {source_name} data...")

        file_path = self.output_dir / filename
        if not file_path.exists():
            logger.warning(f"⚠️  {source_name} data file not found: {filename}")
            return {
                "items": [],
                "duplicates_removed": 0,
                "original_count": 0,
                "final_count": 0,
            }

        try:
            with open(file_path) as f:
                data = json.load(f)

            original_count = len(data)
            seen_hashes = set()
            unique_items = []
            duplicates = []

            for item in data:
                content_hash = self.generate_content_hash(item)

                if content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    unique_items.append(item)
                else:
                    duplicates.append(item)

            # Save deduplicated data
            deduplicated_file = (
                self.deduplicated_dir / f"{source_name.lower()}_deduplicated.json"
            )
            with open(deduplicated_file, "w") as f:
                json.dump(unique_items, f, indent=2, default=str)

            duplicates_removed = original_count - len(unique_items)
            logger.info(
                f"✅ {source_name}: {duplicates_removed} duplicates removed ({original_count} → {len(unique_items)})"
            )

            return {
                "items": unique_items,
                "duplicates_removed": duplicates_removed,
                "original_count": original_count,
                "final_count": len(unique_items),
            }

        except Exception as e:
            logger.error(f"❌ Error deduplicating {source_name} data: {e}")
            return {
                "items": [],
                "duplicates_removed": 0,
                "original_count": 0,
                "final_count": 0,
            }

    def run_deduplication(self):
        """Run deduplication for all data sources"""
        logger.info("🚀 Starting comprehensive deduplication...")

        sources = [
            ("twitter_raw.json", "Twitter"),
            ("reddit_raw.json", "Reddit"),
            ("telegram_raw.json", "Telegram"),
            ("newsapi_raw.json", "News"),
        ]

        results = {}
        for filename, source_name in sources:
            results[source_name.lower()] = self.deduplicate_data_source(
                filename, source_name
            )

        return results

    def create_clean_consolidated_data(self, results: dict[str, Any]):
        """Create clean consolidated data with deduplicated content"""
        logger.info("📦 Creating clean consolidated data...")

        consolidated_data = {
            "tweets": results.get("twitter", {}).get("items", []),
            "reddit_posts": results.get("reddit", {}).get("items", []),
            "telegram_messages": results.get("telegram", {}).get("items", []),
            "news_articles": results.get("news", {}).get("items", []),
            "crypto_data": [],
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "cleanup_date": datetime.now().isoformat(),
                "sources": [],
                "total_items": 0,
                "duplicates_removed": 0,
                "cleanup_version": "1.0",
            },
        }

        # Add crypto data if exists
        crypto_file = self.output_dir / "coingecko_raw.json"
        if crypto_file.exists():
            try:
                with open(crypto_file) as f:
                    consolidated_data["crypto_data"] = json.load(f)
                logger.info("✅ Added crypto data to consolidated file")
            except Exception as e:
                logger.error(f"❌ Error loading crypto data: {e}")

        # Calculate totals
        total_items = 0
        total_duplicates = 0

        for source, data in results.items():
            if data.get("final_count", 0) > 0:
                consolidated_data["metadata"]["sources"].append(source)
                total_items += data.get("final_count", 0)
                total_duplicates += data.get("duplicates_removed", 0)

        consolidated_data["metadata"]["total_items"] = total_items
        consolidated_data["metadata"]["duplicates_removed"] = total_duplicates

        # Save clean consolidated data
        clean_file = self.deduplicated_dir / "consolidated_data_clean.json"
        with open(clean_file, "w") as f:
            json.dump(consolidated_data, f, indent=2, default=str)

        # Also save as main consolidated file
        main_file = self.output_dir / "consolidated_data.json"
        with open(main_file, "w") as f:
            json.dump(consolidated_data, f, indent=2, default=str)

        logger.info(
            f"✅ Clean consolidated data saved: {total_items} items, {total_duplicates} duplicates removed"
        )

        return consolidated_data

    def generate_cleanup_report(
        self, results: dict[str, Any], cache_cleared: int, backup_path: Path
    ):
        """Generate comprehensive cleanup report"""
        logger.info("📊 Generating cleanup report...")

        report = {
            "cleanup_date": datetime.now().isoformat(),
            "summary": {
                "total_duplicates_removed": 0,
                "total_original_items": 0,
                "total_final_items": 0,
                "deduplication_rate": 0.0,
                "cache_locations_cleared": cache_cleared,
                "backup_created": str(backup_path),
            },
            "by_source": {},
            "recommendations": [],
        }

        total_duplicates = 0
        total_original = 0
        total_final = 0

        for source, data in results.items():
            duplicates = data.get("duplicates_removed", 0)
            original = data.get("original_count", 0)
            final = data.get("final_count", 0)

            total_duplicates += duplicates
            total_original += original
            total_final += final

            report["by_source"][source] = {
                "original_count": original,
                "final_count": final,
                "duplicates_removed": duplicates,
                "deduplication_rate": (duplicates / original * 100)
                if original > 0
                else 0,
            }

        report["summary"]["total_duplicates_removed"] = total_duplicates
        report["summary"]["total_original_items"] = total_original
        report["summary"]["total_final_items"] = total_final
        report["summary"]["deduplication_rate"] = (
            (total_duplicates / total_original * 100) if total_original > 0 else 0
        )

        # Generate recommendations
        if total_duplicates > 0:
            report["recommendations"].append(
                f"Removed {total_duplicates} duplicate items ({report['summary']['deduplication_rate']:.1f}% reduction)"
            )

        for source, data in report["by_source"].items():
            if data["deduplication_rate"] > 10:
                report["recommendations"].append(
                    f"High duplication in {source}: {data['deduplication_rate']:.1f}% duplicates"
                )

        if cache_cleared > 0:
            report["recommendations"].append(f"Cleared {cache_cleared} cache locations")

        # Save report
        report_file = self.deduplicated_dir / "cleanup_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"📊 Cleanup report saved to {report_file}")

        return report

    def run_comprehensive_cleanup(self):
        """Run the complete cleanup process"""
        logger.info("🚀 Starting comprehensive data cleanup...")
        print("\n" + "=" * 60)
        print("COMPREHENSIVE DATA CLEANUP")
        print("=" * 60)

        # Step 1: Clear caches
        print("\n1️⃣ Clearing all caches...")
        cache_cleared = self.clear_all_caches()

        # Step 2: Backup original data
        print("\n2️⃣ Creating backup of original data...")
        backup_path = self.backup_original_data()

        # Step 3: Run deduplication
        print("\n3️⃣ Running data deduplication...")
        results = self.run_deduplication()

        # Step 4: Create clean consolidated data
        print("\n4️⃣ Creating clean consolidated data...")
        consolidated_data = self.create_clean_consolidated_data(results)

        # Step 5: Generate report
        print("\n5️⃣ Generating cleanup report...")
        report = self.generate_cleanup_report(results, cache_cleared, backup_path)

        # Print summary
        print("\n" + "=" * 60)
        print("CLEANUP SUMMARY")
        print("=" * 60)

        total_duplicates = report["summary"]["total_duplicates_removed"]
        total_original = report["summary"]["total_original_items"]
        total_final = report["summary"]["total_final_items"]

        print(f"📊 Total Items: {total_original:,} → {total_final:,}")
        print(f"🗑️  Duplicates Removed: {total_duplicates:,}")
        print(f"📈 Deduplication Rate: {report['summary']['deduplication_rate']:.1f}%")
        print(f"🧹 Cache Locations Cleared: {cache_cleared}")
        print(f"💾 Backup Created: {backup_path}")

        print("\n📋 By Source:")
        for source, data in report["by_source"].items():
            print(
                f"  {source.title()}: {data['original_count']:,} → {data['final_count']:,} (-{data['duplicates_removed']:,})"
            )

        print(f"\n📁 Clean files saved in: {self.deduplicated_dir}")
        print("=" * 60)

        return results, consolidated_data, report


def main():
    """Main function to run comprehensive cleanup"""
    cleanup = ComprehensiveDataCleanup()
    results, consolidated_data, report = cleanup.run_comprehensive_cleanup()

    print("\n🎉 Comprehensive cleanup completed successfully!")
    print("✅ Your data is now clean and deduplicated")
    print("✅ Caches have been cleared")
    print("✅ Backup has been created")
    print("✅ Dashboard should work without errors")
    print("\nYou can now restart the dashboard: streamlit run dashboard/app.py")


if __name__ == "__main__":
    main()
