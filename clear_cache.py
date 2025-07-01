#!/usr/bin/env python3
"""
Clear all caches to fix dashboard issues
"""

import shutil
import os
from pathlib import Path
import sqlite3

def clear_all_caches():
    """Clear all cache files and directories"""
    print("🧹 Clearing all caches...")
    
    # Clear Streamlit cache
    streamlit_cache = Path.home() / ".streamlit" / "cache"
    if streamlit_cache.exists():
        try:
            shutil.rmtree(streamlit_cache)
            print(f"✅ Cleared Streamlit cache: {streamlit_cache}")
        except Exception as e:
            print(f"❌ Error clearing Streamlit cache: {e}")
    
    # Clear LLM cache
    llm_cache = Path("output/llm_cache.sqlite")
    if llm_cache.exists():
        try:
            llm_cache.unlink()
            print(f"✅ Cleared LLM cache: {llm_cache}")
        except Exception as e:
            print(f"❌ Error clearing LLM cache: {e}")
    
    # Clear any .cache directories
    cache_dirs = [
        Path("output/.cache"),
        Path("dashboard/.cache"),
        Path(".cache")
    ]
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            try:
                shutil.rmtree(cache_dir)
                print(f"✅ Cleared cache directory: {cache_dir}")
            except Exception as e:
                print(f"❌ Error clearing {cache_dir}: {e}")
    
    # Clear __pycache__ directories
    pycache_dirs = list(Path(".").rglob("__pycache__"))
    for pycache in pycache_dirs:
        try:
            shutil.rmtree(pycache)
            print(f"✅ Cleared __pycache__: {pycache}")
        except Exception as e:
            print(f"❌ Error clearing {pycache}: {e}")
    
    print("\n🎉 Cache clearing completed!")
    print("You can now restart the dashboard.")

if __name__ == "__main__":
    clear_all_caches() 