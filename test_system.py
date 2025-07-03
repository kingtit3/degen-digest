#!/usr/bin/env python3
"""
Comprehensive system test for Degen Digest
Tests all components and identifies issues
"""

import sqlite3
from pathlib import Path

import requests


def test_database():
    """Test database connectivity and data"""
    print("🔍 Testing Database...")

    try:
        db_path = Path("output/degen_digest.db")
        if not db_path.exists():
            print("❌ Database file not found")
            return False

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables: {[t[0] for t in tables]}")

        # Check data counts
        for table in ["Tweet", "RedditPost", "Digest"]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   📊 {table}: {count} records")
            except Exception as e:
                print(f"   ❌ {table}: Error - {e}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_data_files():
    """Test data files existence and content"""
    print("\n📁 Testing Data Files...")

    data_files = [
        "output/digest.md",
        "output/consolidated_data.json",
        "output/twitter_raw.json",
        "output/reddit_raw.json",
        "output/newsapi_raw.json",
    ]

    for file_path in data_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {file_path}: {size:,} bytes")
        else:
            print(f"❌ {file_path}: Not found")

    return True


def test_cloud_function():
    """Test cloud function connectivity"""
    print("\n☁️ Testing Cloud Function...")

    try:
        url = "https://us-central1-lucky-union-463615-t3.cloudfunctions.net/degen-digest-refresh"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            print("✅ Cloud function is accessible")
            return True
        else:
            print(f"❌ Cloud function returned status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Cloud function test failed: {e}")
        return False


def test_dashboard_files():
    """Test dashboard file structure"""
    print("\n🎯 Testing Dashboard Files...")

    required_files = [
        "dashboard/main.py",
        "dashboard/app.py",
        "dashboard/pages/Analytics.py",
        "dashboard/pages/Digests.py",
        "dashboard/pages/Live_Feed.py",
    ]

    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}: Found")
        else:
            print(f"❌ {file_path}: Missing")

    return True


def test_environment():
    """Test environment variables and configuration"""
    print("\n⚙️ Testing Environment...")

    try:
        from utils.env import get_env_var

        # Test key environment variables
        env_vars = ["APIFY_API_TOKEN", "NEWSAPI_KEY"]
        for var in env_vars:
            value = get_env_var(var)
            if value:
                print(f"✅ {var}: Set (length: {len(value)})")
            else:
                print(f"❌ {var}: Not set")

        return True

    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False


def generate_fix_plan():
    """Generate a plan to fix identified issues"""
    print("\n🔧 GENERATING FIX PLAN...")
    print("=" * 50)

    print("1. 🚀 IMMEDIATE ACTIONS:")
    print("   - Run: python fetch_todays_digest.py")
    print("   - Run: streamlit run dashboard/main.py --server.port 8501")

    print("\n2. 📊 DATA COLLECTION:")
    print("   - Deploy updated cloud function")
    print("   - Test with real API keys")
    print("   - Verify data is being saved")

    print("\n3. 🎯 DASHBOARD FIXES:")
    print("   - Ensure all page modules are working")
    print("   - Fix any import errors")
    print("   - Test data visualization")

    print("\n4. 🔄 AUTOMATION:")
    print("   - Set up scheduled digest generation")
    print("   - Configure data sync")
    print("   - Monitor system health")

    print("\n5. 📈 OPTIMIZATION:")
    print("   - Improve data processing")
    print("   - Enhance UI/UX")
    print("   - Add new features")


def main():
    """Run all system tests"""
    print("🚀 Degen Digest System Test")
    print("=" * 50)

    tests = [
        test_database,
        test_data_files,
        test_cloud_function,
        test_dashboard_files,
        test_environment,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")

    if all(results):
        print("\n🎉 All tests passed! System is ready.")
    else:
        print("\n⚠️ Some tests failed. Generating fix plan...")
        generate_fix_plan()


if __name__ == "__main__":
    main()
