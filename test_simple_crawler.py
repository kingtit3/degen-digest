#!/usr/bin/env python3
"""
Simple test crawler that just prints and exits
"""

import logging
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Main function"""
    logger.info("🚀 Simple test crawler starting...")
    logger.info(f"📅 Current time: {datetime.now()}")
    logger.info("✅ Simple test crawler completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
