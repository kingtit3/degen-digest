#!/usr/bin/env python3
"""
Test script for the new Degen Digest Dashboard
"""

import sys
from pathlib import Path


def test_dashboard_functions():
    """Test the dashboard functions"""
    print("🧪 Testing New Dashboard Functions")
    print("=" * 40)

    # Add current directory to path
    sys.path.insert(0, str(Path(__file__).parent))

    try:
        # Import dashboard functions
        from dashboard.app import get_latest_digest, get_raw_data, get_trending_content

        print("✅ Successfully imported dashboard functions")

        # Test get_latest_digest
        print("\n📄 Testing get_latest_digest()...")
        content, filename = get_latest_digest()
        if content:
            print(f"✅ Found digest: {filename}")
            print(f"📊 Content length: {len(content)} characters")
        else:
            print(f"⚠️ {filename}")

        # Test get_raw_data
        print("\n📊 Testing get_raw_data()...")
        data = get_raw_data()
        total_items = sum(
            len(items) if isinstance(items, list) else 0 for items in data.values()
        )
        print(f"✅ Loaded {total_items} total items from {len(data)} sources")

        for source, items in data.items():
            if isinstance(items, list):
                print(f"   - {source}: {len(items)} items")

        # Test get_trending_content
        print("\n🔥 Testing get_trending_content()...")
        trending = get_trending_content(data, limit=5)
        print(f"✅ Found {len(trending)} trending items")

        if trending:
            print("📋 Sample trending items:")
            for i, item in enumerate(trending[:3], 1):
                print(
                    f"   {i}. {item['source']} - Score: {item['engagement_score']:.1f}"
                )

        print("\n🎉 All dashboard functions working correctly!")
        return True

    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_dashboard_requirements():
    """Test if required packages are available"""
    print("\n📦 Testing Dashboard Requirements")
    print("=" * 40)

    required_packages = ["streamlit", "pandas", "plotly", "sqlmodel"]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r requirements-streamlit.txt")
        return False
    else:
        print("\n✅ All required packages available!")
        return True


def main():
    """Main test function"""
    print("🚀 Testing New Degen Digest Dashboard")
    print("=" * 50)

    # Test requirements
    req_ok = test_dashboard_requirements()

    # Test functions
    func_ok = test_dashboard_functions()

    print("\n" + "=" * 50)
    if req_ok and func_ok:
        print("🎉 Dashboard is ready to use!")
        print("💡 Start with: python3 start_dashboard.py")
    else:
        print("⚠️ Some issues found. Check the output above.")

    return req_ok and func_ok


if __name__ == "__main__":
    main()
