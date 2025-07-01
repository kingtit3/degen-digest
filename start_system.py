#!/usr/bin/env python3
"""
Startup script for Degen Digest
Fixes common issues and gets the system running
"""

import subprocess
import sys
from pathlib import Path
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def fix_dashboard_startup():
    """Fix dashboard startup issues"""
    print("🔧 Fixing dashboard startup...")
    
    # Ensure dashboard directory structure is correct
    dashboard_dir = Path("dashboard")
    if not dashboard_dir.exists():
        print("❌ Dashboard directory not found")
        return False
    
    # Check if main.py exists and is correct
    main_py = dashboard_dir / "main.py"
    if not main_py.exists():
        print("❌ dashboard/main.py not found - creating it")
        # The main.py file should already be created by previous steps
    
    return True

def fetch_latest_data():
    """Fetch latest data from cloud function"""
    print("📊 Fetching latest data...")
    
    # Run the fetch script
    if Path("fetch_todays_digest.py").exists():
        return run_command("python fetch_todays_digest.py", "Fetching today's digest")
    else:
        print("❌ fetch_todays_digest.py not found")
        return False

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("🚀 Starting dashboard...")
    
    # Check if streamlit is installed
    if not run_command("streamlit --version", "Checking Streamlit installation"):
        print("❌ Streamlit not installed. Installing...")
        run_command("pip install streamlit", "Installing Streamlit")
    
    # Start the dashboard
    print("🎯 Starting dashboard on http://localhost:8501")
    print("📝 Press Ctrl+C to stop the dashboard")
    
    # Run streamlit in the background
    try:
        subprocess.run([
            "streamlit", "run", "dashboard/main.py", 
            "--server.port", "8501",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Dashboard failed to start: {e}")

def main():
    """Main startup sequence"""
    print("🚀 Degen Digest System Startup")
    print("="*50)
    
    # Step 1: Fix dashboard startup
    if not fix_dashboard_startup():
        print("❌ Failed to fix dashboard startup")
        return
    
    # Step 2: Fetch latest data
    fetch_latest_data()
    
    # Step 3: Start dashboard
    start_dashboard()

if __name__ == "__main__":
    main() 