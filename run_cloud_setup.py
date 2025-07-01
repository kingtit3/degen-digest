#!/usr/bin/env python3
"""
Automated Cloud Setup Script for Degen Digest
Runs all the necessary steps to set up Google Cloud Storage integration.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description, timeout=60):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - EXCEPTION: {e}")
        return False

def main():
    """Main function to run all cloud setup steps"""
    print("🚀 Degen Digest Cloud Setup Automation")
    print("=" * 50)
    
    # Step 1: Check Python and dependencies
    print("\n📋 Step 1: Checking Python environment...")
    
    if not run_command("python --version", "Check Python version"):
        print("❌ Python not available. Please ensure Python is installed.")
        return False
    
    if not run_command("pip list | grep google-cloud-storage", "Check Google Cloud Storage"):
        print("⚠️  Google Cloud Storage not found. Installing...")
        if not run_command("pip install google-cloud-storage", "Install Google Cloud Storage"):
            print("❌ Failed to install Google Cloud Storage")
            return False
    
    # Step 2: Test cloud setup
    print("\n📋 Step 2: Testing cloud setup...")
    
    if not run_command("python test_cloud_setup.py", "Test cloud setup"):
        print("⚠️  Cloud setup test failed. This might be due to authentication.")
    
    # Step 3: Check Google Cloud authentication
    print("\n📋 Step 3: Checking Google Cloud authentication...")
    
    if not run_command("gcloud auth list", "Check current authentication"):
        print("⚠️  No authentication found. You may need to run: gcloud auth application-default login")
    
    # Step 4: Set project
    print("\n📋 Step 4: Setting Google Cloud project...")
    
    if not run_command("gcloud config set project lucky-union-463615-t3", "Set project ID"):
        print("⚠️  Failed to set project. You may need to authenticate first.")
    
    # Step 5: Verify project
    print("\n📋 Step 5: Verifying project configuration...")
    
    if not run_command("gcloud config get-value project", "Verify project ID"):
        print("⚠️  Could not verify project ID")
    
    # Step 6: Run data merger
    print("\n📋 Step 6: Running data merger...")
    
    if not run_command("python scripts/merge_local_cloud_data.py", "Merge local data"):
        print("❌ Data merger failed")
        return False
    
    # Step 7: Upload to cloud
    print("\n📋 Step 7: Uploading data to cloud...")
    
    if not run_command("python scripts/cloud_storage_sync.py --direction upload", "Upload to cloud"):
        print("⚠️  Cloud upload failed. This might be due to authentication issues.")
    
    # Step 8: List cloud files
    print("\n📋 Step 8: Listing cloud files...")
    
    if not run_command("python scripts/cloud_storage_sync.py --list", "List cloud files"):
        print("⚠️  Could not list cloud files")
    
    # Step 9: Create database backup
    print("\n📋 Step 9: Creating database backup...")
    
    if not run_command("python scripts/cloud_storage_sync.py --backup", "Create database backup"):
        print("⚠️  Database backup failed")
    
    print("\n" + "=" * 50)
    print("🎉 Cloud Setup Automation Complete!")
    print("\n📊 Summary:")
    print("✅ Python environment checked")
    print("✅ Dependencies verified")
    print("✅ Data merger completed")
    print("⚠️  Cloud operations may need manual authentication")
    
    print("\n🔧 Next Steps:")
    print("1. If authentication failed, run: gcloud auth application-default login")
    print("2. Test cloud setup: python test_cloud_setup.py")
    print("3. Upload data: python scripts/cloud_storage_sync.py --direction upload")
    print("4. Launch dashboard: streamlit run dashboard/app.py")
    
    print("\n📁 Check these files:")
    print("- output/consolidated_data.json (should exist)")
    print("- output/merge_report.json (should exist)")
    print("- output/dashboard_processed_data.json (should exist)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 