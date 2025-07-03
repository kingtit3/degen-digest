#!/usr/bin/env python3
"""
Main entry point for the Degen Digest Dashboard
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import and run the main app
from dashboard.app import main

if __name__ == "__main__":
    main()
