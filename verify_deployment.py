#!/usr/bin/env python3
"""
Deployment Verification Script for Degen Digest
Tests all deployed services and components
"""

import requests
import json
import time
from datetime import datetime
import sys

# Deployment URLs
DASHBOARD_URL = "https://degen-digest-dashboard-6if5kdcbiq-uc.a.run.app"
CLOUD_FUNCTION_URL = "https://us-central1-lucky-union-463615-t3.cloudfunctions.net/refresh_data"

def test_dashboard():
    """Test the Streamlit dashboard"""
    print("🔍 Testing Dashboard...")
    try:
        response = requests.get(DASHBOARD_URL, timeout=30)
        if response.status_code == 200:
            print("✅ Dashboard is accessible and responding")
            return True
        else:
            print(f"❌ Dashboard returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_cloud_function():
    """Test the cloud function"""
    print("🔍 Testing Cloud Function...")
    try:
        response = requests.get(CLOUD_FUNCTION_URL, timeout=60)
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Cloud function is working correctly")
                print(f"   Message: {result.get('message')}")
                print(f"   Timestamp: {result.get('timestamp')}")
                return True
            else:
                print(f"❌ Cloud function returned error: {result.get('message')}")
                return False
        else:
            print(f"❌ Cloud function returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cloud function test failed: {e}")
        return False

def test_data_refresh():
    """Test the data refresh functionality"""
    print("🔍 Testing Data Refresh...")
    try:
        # Trigger a data refresh
        response = requests.post(CLOUD_FUNCTION_URL, timeout=300)
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Data refresh completed successfully")
                return True
            else:
                print(f"❌ Data refresh failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Data refresh returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Data refresh test failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 Degen Digest Deployment Verification")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # Test results
    tests = {
        "Dashboard": test_dashboard(),
        "Cloud Function": test_cloud_function(),
        "Data Refresh": test_data_refresh()
    }
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Deployment is successful.")
        print("\n📋 Service URLs:")
        print(f"   Dashboard: {DASHBOARD_URL}")
        print(f"   Cloud Function: {CLOUD_FUNCTION_URL}")
        print("\n📝 Next Steps:")
        print("   1. Open the dashboard URL in your browser")
        print("   2. Verify all pages and features are working")
        print("   3. Test the data refresh functionality")
        print("   4. Monitor logs for any issues")
    else:
        print("⚠️  Some tests failed. Please check the deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main() 