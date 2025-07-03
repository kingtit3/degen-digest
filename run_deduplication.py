#!/usr/bin/env python3
"""
Simple script to run data deduplication
"""

import os
import sys

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))

try:
    from deduplicate_data import DataDeduplicator

    print("Starting data deduplication...")
    deduplicator = DataDeduplicator()
    results, consolidated_data, report = deduplicator.run_deduplication()

    print("\n🎉 Deduplication completed successfully!")
    print("Check the 'output/deduplicated' directory for results.")

except ImportError as e:
    print(f"Import error: {e}")
    print(
        "Make sure you're in the correct directory and all dependencies are installed."
    )
except Exception as e:
    print(f"Error running deduplication: {e}")
    import traceback

    traceback.print_exc()
