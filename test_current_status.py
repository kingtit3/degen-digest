#!/usr/bin/env python3
"""
Test current status of the Degen Digest system
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path


def check_current_status():
    """Check the current status of the system"""
    print("🔍 Current System Status")
    print("=" * 40)

    # Check database
    db_path = Path("output/degen_digest.db")
    if db_path.exists():
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

            print("📊 Database Contents:")
            print(f"   - Tweets: {tweet_count}")
            print(f"   - Reddit posts: {reddit_count}")
            print(f"   - Digests: {digest_count}")

        except Exception as e:
            print(f"❌ Database error: {e}")
    else:
        print("❌ Database not found")

    # Check digest files
    output_dir = Path("output")
    digest_files = list(output_dir.glob("digest*.md"))
    print(f"\n📄 Digest Files: {len(digest_files)}")
    for file in digest_files:
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        print(f"   - {file.name} (modified: {mtime.strftime('%Y-%m-%d %H:%M')})")

    # Check raw data files
    raw_files = ["twitter_raw.json", "reddit_raw.json", "newsapi_raw.json"]
    print("\n📊 Raw Data Files:")
    for file in raw_files:
        file_path = output_dir / file
        if file_path.exists():
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    print(f"   - {file}: {len(data)} items")
            except Exception as e:
                print(f"   - {file}: Error reading ({e})")
        else:
            print(f"   - {file}: Not found")

    # Check consolidated data
    consolidated_path = output_dir / "consolidated_data.json"
    if consolidated_path.exists():
        size_mb = consolidated_path.stat().st_size / (1024 * 1024)
        print(f"\n📈 Consolidated Data: {size_mb:.1f} MB")
    else:
        print("\n❌ Consolidated data not found")

    # Check if system is working
    print("\n🎯 System Status:")
    if reddit_count > 0 or digest_count > 0:
        print("   ✅ System is working - data is being collected and processed")
    else:
        print("   ❌ System is not working - no data found")

    if digest_files:
        print("   ✅ Digests are being generated")
    else:
        print("   ❌ No digests found")


if __name__ == "__main__":
    check_current_status()
