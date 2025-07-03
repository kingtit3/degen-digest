#!/usr/bin/env python3
"""
Test Google Cloud Storage Setup
Verifies the cloud storage configuration with the correct project ID.
"""

import sys
from pathlib import Path


def test_gcs_setup():
    """Test Google Cloud Storage setup"""
    print("🔍 Testing Google Cloud Storage Setup...")

    # Test imports
    try:
        from google.cloud import storage

        print("✅ Google Cloud Storage import successful")
    except ImportError as e:
        print(f"❌ Google Cloud Storage import failed: {e}")
        print("Install with: pip install google-cloud-storage")
        return False

    # Test authentication
    try:
        project_id = "lucky-union-463615-t3"
        client = storage.Client(project=project_id)
        print(f"✅ Authentication successful for project: {project_id}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print(
            "Make sure you're authenticated with: gcloud auth application-default login"
        )
        return False

    # Test bucket access
    try:
        bucket_name = "degen-digest-data"
        bucket = client.bucket(bucket_name)

        if bucket.exists():
            print(f"✅ Bucket '{bucket_name}' exists")

            # List files
            blobs = list(bucket.list_blobs(max_results=10))
            print(f"📁 Found {len(blobs)} files in bucket")
            for blob in blobs[:5]:
                print(f"   - {blob.name}")
        else:
            print(f"⚠️  Bucket '{bucket_name}' doesn't exist, will create it")
            bucket.create(project=project_id)
            print(f"✅ Created bucket '{bucket_name}'")

    except Exception as e:
        print(f"❌ Bucket access failed: {e}")
        return False

    return True


def test_local_data():
    """Test local data files"""
    print("\n📁 Testing Local Data Files...")

    output_dir = Path("output")
    if not output_dir.exists():
        print("❌ Output directory not found")
        return False

    important_files = [
        "consolidated_data.json",
        "dashboard_processed_data.json",
        "twitter_raw.json",
        "reddit_raw.json",
        "telegram_raw.json",
    ]

    found_files = 0
    for filename in important_files:
        file_path = output_dir / filename
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"✅ {filename}: {size_mb:.2f} MB")
            found_files += 1
        else:
            print(f"❌ {filename}: Missing")

    print(f"📊 Found {found_files}/{len(important_files)} important files")
    return found_files > 0


def main():
    """Main test function"""
    print("🚀 Degen Digest Cloud Storage Test")
    print("=" * 50)

    # Test GCS setup
    gcs_ok = test_gcs_setup()

    # Test local data
    local_ok = test_local_data()

    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"Google Cloud Storage: {'✅ Ready' if gcs_ok else '❌ Issues'}")
    print(f"Local Data: {'✅ Ready' if local_ok else '❌ Issues'}")

    if gcs_ok and local_ok:
        print("\n🎉 All tests passed! You can now use cloud storage sync.")
        print("\nNext steps:")
        print("1. python scripts/cloud_storage_sync.py --list")
        print("2. python scripts/cloud_storage_sync.py --direction upload")
        print("3. Check the Data Sync dashboard page")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")

    return gcs_ok and local_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
