#!/usr/bin/env python3
"""
Degen Digest Dashboard - Main Streamlit App
Deploy this to Streamlit Cloud for easy hosting
"""

import sys
from pathlib import Path

# Add the project root to Python path
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

# Import and run the dashboard app
from dashboard.app import main

if __name__ == "__main__":
    main() 