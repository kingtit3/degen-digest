#!/usr/bin/env python3
"""
Restart Dashboard and Clear Cache
"""

import os
import subprocess
import time
import signal
import psutil

def kill_streamlit_processes():
    """Kill any running Streamlit processes"""
    print("🔄 Stopping existing Streamlit processes...")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'streamlit' or 'streamlit' in ' '.join(proc.info['cmdline'] or []):
                print(f"Stopping process {proc.info['pid']}")
                proc.terminate()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            pass

def clear_cache():
    """Clear Streamlit cache"""
    print("🧹 Clearing cache...")
    
    import shutil
    from pathlib import Path
    
    # Clear .streamlit cache
    streamlit_cache = Path.home() / ".streamlit" / "cache"
    if streamlit_cache.exists():
        shutil.rmtree(streamlit_cache)
        print("✅ Cleared Streamlit cache")
    
    # Clear any local cache
    local_cache = Path("output") / ".cache"
    if local_cache.exists():
        shutil.rmtree(local_cache)
        print("✅ Cleared local cache")

def restart_dashboard():
    """Restart the dashboard"""
    print("🚀 Starting dashboard...")
    
    # Kill existing processes
    kill_streamlit_processes()
    
    # Clear cache
    clear_cache()
    
    # Wait a moment
    time.sleep(2)
    
    # Start dashboard
    try:
        subprocess.Popen([
            "streamlit", "run", "dashboard/app.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
        print("✅ Dashboard started on http://localhost:8501")
        print("📱 You can now access the new Top Items page!")
        
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        print("Try running manually: streamlit run dashboard/app.py")

def main():
    """Main function"""
    print("🔄 Dashboard Restart Tool")
    print("=" * 40)
    
    restart_dashboard()
    
    print("\n🎉 Complete!")
    print("The dashboard should now be running without errors.")
    print("Check out the new 'Top Items' page for Twitter-like interface!")

if __name__ == "__main__":
    main() 