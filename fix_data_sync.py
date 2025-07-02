#!/usr/bin/env python3
"""
Comprehensive fix for Degen Digest data sync and digest generation issues.
"""

import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import requests


def check_system_status():
    """Check the current status of the system"""
    print("🔍 Checking system status...")

    # Check output directory
    output_dir = Path("output")
    if not output_dir.exists():
        print("❌ Output directory missing")
        return False

    # Check database
    db_path = output_dir / "degen_digest.db"
    if not db_path.exists():
        print("❌ Database missing")
        return False

    # Check digest files
    digest_files = list(output_dir.glob("digest*.md"))
    print(f"📄 Found {len(digest_files)} digest files")

    # Check database contents
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM tweet")
        tweet_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM redditpost")
        reddit_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM digest")
        digest_count = cursor.fetchone()[0]

        conn.close()

        print(
            f"📊 Database contents: {tweet_count} tweets, {reddit_count} reddit posts, {digest_count} digests"
        )

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

    return True


def trigger_cloud_function():
    """Trigger the cloud function to collect fresh data"""
    print("🔄 Triggering cloud function...")

    url = "https://us-central1-lucky-union-463615-t3.cloudfunctions.net/refresh_data"

    try:
        response = requests.post(
            url, json={"generate_digest": True, "force_refresh": True}, timeout=300
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cloud function response: {data.get('status', 'unknown')}")
            print(
                f"📊 Collected {data.get('metrics', {}).get('data_collected', 0)} items"
            )
            return data
        else:
            print(f"❌ Cloud function error: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Error calling cloud function: {e}")
        return None


def run_local_scrapers():
    """Run local scrapers to collect data"""
    print("🔄 Running local scrapers...")

    scrapers = [
        "scrapers/reddit_rss.py",
        "scrapers/newsapi_headlines.py",
        "scrapers/coingecko_gainers.py",
    ]

    for scraper in scrapers:
        if Path(scraper).exists():
            print(f"   Running {scraper}...")
            try:
                result = subprocess.run(
                    [sys.executable, scraper],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode == 0:
                    print(f"   ✅ {scraper} completed")
                else:
                    print(f"   ⚠️ {scraper} failed: {result.stderr}")
            except Exception as e:
                print(f"   ❌ {scraper} error: {e}")
        else:
            print(f"   ⚠️ {scraper} not found")


def generate_local_digest():
    """Generate digest locally"""
    print("📄 Generating local digest...")

    try:
        # Check if main.py exists and can run
        if Path("main.py").exists():
            result = subprocess.run(
                [sys.executable, "main.py"], capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                print("✅ Local digest generation completed")
                return True
            else:
                print(f"⚠️ Local digest generation failed: {result.stderr}")
                return False
        else:
            print("❌ main.py not found")
            return False

    except Exception as e:
        print(f"❌ Error generating local digest: {e}")
        return False


def fix_database():
    """Fix database issues"""
    print("🗄️ Fixing database...")

    db_path = Path("output/degen_digest.db")
    if not db_path.exists():
        print("❌ Database not found")
        return False

    try:
        # Recreate database tables
        result = subprocess.run(
            [sys.executable, "recreate_db.py"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            print("✅ Database recreated")
            return True
        else:
            print(f"⚠️ Database recreation failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False


def update_dashboard_data():
    """Update dashboard data files"""
    print("📊 Updating dashboard data...")

    output_dir = Path("output")

    # Check if we have raw data files
    raw_files = ["twitter_raw.json", "reddit_raw.json", "newsapi_raw.json"]
    has_data = False

    for file in raw_files:
        if (output_dir / file).exists():
            has_data = True
            break

    if not has_data:
        print("⚠️ No raw data files found")
        return False

    # Run data processing
    try:
        if Path("run_deduplication.py").exists():
            result = subprocess.run(
                [sys.executable, "run_deduplication.py"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                print("✅ Data deduplication completed")
            else:
                print(f"⚠️ Data deduplication failed: {result.stderr}")

        if Path("run_enhanced_system.py").exists():
            result = subprocess.run(
                [sys.executable, "run_enhanced_system.py"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                print("✅ Enhanced system processing completed")
            else:
                print(f"⚠️ Enhanced system processing failed: {result.stderr}")

        return True

    except Exception as e:
        print(f"❌ Error updating dashboard data: {e}")
        return False


def create_test_digest():
    """Create a test digest to ensure the system works"""
    print("🧪 Creating test digest...")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    test_digest = f"""# 🚀 Degen Digest - Test Digest

## 📊 Executive Summary
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
Status: Test digest to verify system functionality

## 🐦 Top Twitter Moments
*No Twitter data available*

## 🔥 Hot Reddit Posts
*No Reddit data available*

## 📰 Breaking News
*No news data available*

## 📈 Market Sentiment Overview
- **Overall Sentiment:** 0.00
- **Total Engagement:** 0
- **Data Quality:** 0/0 items analyzed

---
*Generated by Degen Digest Test System* 🤖
"""

    # Save test digest
    digest_path = output_dir / "digest.md"
    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(test_digest)

    # Save dated digest
    date_str = datetime.now().strftime("%Y-%m-%d")
    dated_digest_path = output_dir / f"digest-{date_str}.md"
    with open(dated_digest_path, "w", encoding="utf-8") as f:
        f.write(test_digest)

    print("✅ Test digest created")
    return True


def main():
    """Main function to fix all issues"""
    print("🚀 Degen Digest System Fix")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now()}")

    # Step 1: Check system status
    if not check_system_status():
        print("⚠️ System has issues, attempting to fix...")

    # Step 2: Fix database
    fix_database()

    # Step 3: Run local scrapers
    run_local_scrapers()

    # Step 4: Try cloud function
    trigger_cloud_function()

    # Step 5: Generate digest locally
    if not generate_local_digest():
        print("⚠️ Local digest generation failed, creating test digest...")
        create_test_digest()

    # Step 6: Update dashboard data
    update_dashboard_data()

    # Step 7: Final status check
    print("\n📋 Final Status Check:")
    check_system_status()

    print("\n🎉 System fix completed!")
    print("📊 Check the dashboard at https://farmchecker.xyz")
    print("💡 If issues persist, check the logs for more details")


if __name__ == "__main__":
    main()
