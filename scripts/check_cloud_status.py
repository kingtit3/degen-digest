#!/usr/bin/env python3
"""
Cloud Status Checker
Comprehensive status check for all cloud-based components.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import requests

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.cloud_config import get_config, get_gcs_client_config

try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("❌ Google Cloud Storage not available")


def check_gcs_connection():
    """Check Google Cloud Storage connection"""
    print("🔍 Checking Google Cloud Storage...")

    if not GCS_AVAILABLE:
        print("❌ GCS not available")
        return False

    try:
        gcs_config = get_gcs_client_config()
        client = storage.Client(project=gcs_config["project_id"])
        bucket = client.bucket(gcs_config["bucket_name"])

        # Test bucket access
        if bucket.exists():
            print(f"✅ GCS bucket accessible: {gcs_config['bucket_name']}")
            return True
        else:
            print(f"❌ GCS bucket not found: {gcs_config['bucket_name']}")
            return False

    except Exception as e:
        print(f"❌ GCS connection failed: {e}")
        return False


def check_crawler_status():
    """Check crawler service status"""
    print("🔍 Checking Crawler Service...")

    config = get_config()
    crawler_url = config.get_service_url("crawler")

    if not crawler_url:
        print("❌ Crawler URL not configured")
        return False

    try:
        response = requests.get(f"{crawler_url}/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            status = status_data.get("status", "unknown")
            print(f"✅ Crawler Status: {status}")

            if "session_stats" in status_data:
                stats = status_data["session_stats"]
                print(f"   📊 Total Crawls: {stats.get('total_crawls', 0)}")
                print(f"   📊 Successful Crawls: {stats.get('successful_crawls', 0)}")
                print(f"   📊 Total Tweets: {stats.get('total_tweets_collected', 0)}")

            return status == "running"
        else:
            print(f"❌ Crawler returned HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Crawler check failed: {e}")
        return False


def check_dashboard_status():
    """Check dashboard service status"""
    print("🔍 Checking Dashboard Service...")

    config = get_config()
    dashboard_url = config.get_service_url("dashboard")

    if not dashboard_url:
        print("❌ Dashboard URL not configured")
        return False

    try:
        response = requests.get(dashboard_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Dashboard accessible: {dashboard_url}")
            return True
        else:
            print(f"❌ Dashboard returned HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Dashboard check failed: {e}")
        return False


def check_data_structure():
    """Check data structure in GCS"""
    print("🔍 Checking Data Structure...")

    if not GCS_AVAILABLE:
        print("❌ GCS not available")
        return False

    try:
        gcs_config = get_gcs_client_config()
        client = storage.Client(project=gcs_config["project_id"])
        bucket = client.bucket(gcs_config["bucket_name"])

        config = get_config()

        # Check raw data directories
        raw_sources = ["twitter", "reddit", "telegram", "news", "crypto"]
        for source in raw_sources:
            raw_path = config.get_raw_data_path(source)
            blobs = list(bucket.list_blobs(prefix=raw_path))
            file_count = len([b for b in blobs if b.name.endswith(".json")])
            print(f"   📁 {source.title()} Raw Data: {file_count} files")

        # Check consolidated data
        print("\n📊 Consolidated Data:")
        for source in raw_sources:
            consolidated_path = config.get_consolidated_path(source)
            blob = bucket.blob(consolidated_path)
            if blob.exists():
                try:
                    content = blob.download_as_text()
                    data = json.loads(content)
                    if "tweets" in data:
                        count = len(data["tweets"])
                    elif "data" in data:
                        count = len(data["data"])
                    else:
                        count = 0
                    print(f"   ✅ {source.title()}: {count} items")
                except Exception as e:
                    print(f"   ❌ {source.title()}: Error reading ({e})")
            else:
                print(f"   ⚠️ {source.title()}: Not found")

        # Check analytics
        print("\n📈 Analytics:")
        analytics_types = ["crawler_stats", "engagement_metrics"]
        for analytics_type in analytics_types:
            analytics_path = config.get_analytics_path(analytics_type)
            blob = bucket.blob(analytics_path)
            if blob.exists():
                print(f"   ✅ {analytics_type}: Available")
            else:
                print(f"   ⚠️ {analytics_type}: Not found")

        return True

    except Exception as e:
        print(f"❌ Data structure check failed: {e}")
        return False


def check_recent_activity():
    """Check for recent data collection activity"""
    print("🔍 Checking Recent Activity...")

    if not GCS_AVAILABLE:
        print("❌ GCS not available")
        return False

    try:
        gcs_config = get_gcs_client_config()
        client = storage.Client(project=gcs_config["project_id"])
        bucket = client.bucket(gcs_config["bucket_name"])

        # Check Twitter data for recent files
        twitter_files = list(bucket.list_blobs(prefix="twitter_data/"))
        recent_files = []

        for blob in twitter_files:
            if blob.name.endswith(".json"):
                # Get file metadata
                blob.reload()
                updated = blob.updated
                if updated:
                    recent_files.append((blob.name, updated))

        # Sort by update time
        recent_files.sort(key=lambda x: x[1], reverse=True)

        if recent_files:
            latest_file, latest_time = recent_files[0]
            print(f"✅ Latest Twitter data: {latest_file}")
            print(f"   📅 Updated: {latest_time}")

            # Check if it's recent (within last hour)
            time_diff = datetime.now(latest_time.tzinfo) - latest_time
            if time_diff.total_seconds() < 3600:  # 1 hour
                print("   🟢 Recent activity detected")
                return True
            else:
                print(f"   ⚠️ No recent activity (last update: {time_diff})")
                return False
        else:
            print("❌ No Twitter data files found")
            return False

    except Exception as e:
        print(f"❌ Recent activity check failed: {e}")
        return False


def generate_status_report():
    """Generate comprehensive status report"""
    print("🚀 Degen Digest Cloud Status Report")
    print("=" * 50)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Configuration check
    config = get_config()
    config.print_summary()
    print()

    # Service checks
    gcs_ok = check_gcs_connection()
    print()

    crawler_ok = check_crawler_status()
    print()

    dashboard_ok = check_dashboard_status()
    print()

    data_ok = check_data_structure()
    print()

    activity_ok = check_recent_activity()
    print()

    # Summary
    print("=" * 50)
    print("📋 STATUS SUMMARY")
    print("=" * 50)

    status_items = [
        ("Google Cloud Storage", gcs_ok),
        ("Crawler Service", crawler_ok),
        ("Dashboard Service", dashboard_ok),
        ("Data Structure", data_ok),
        ("Recent Activity", activity_ok),
    ]

    all_ok = True
    for item, status in status_items:
        icon = "✅" if status else "❌"
        print(f"{icon} {item}")
        if not status:
            all_ok = False

    print()
    if all_ok:
        print("🎉 All systems operational!")
        print("🌐 Dashboard: https://farmchecker-128671663649.us-central1.run.app")
        print("🤖 Crawler: https://solana-crawler-128671663649.us-central1.run.app")
    else:
        print("⚠️ Some issues detected. Check the details above.")

    return all_ok


def main():
    """Main function"""
    try:
        success = generate_status_report()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Status check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Status check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
