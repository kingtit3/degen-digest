#!/usr/bin/env python3
"""
Test script for crawler status table
"""

import os
import psycopg2
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "34.9.71.174"),
    "database": os.getenv("DB_NAME", "degen_digest"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "DegenDigest2024!"),
    "port": os.getenv("DB_PORT", "5432"),
}

def test_crawler_status():
    """Test the crawler status table functionality"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Test 1: Check if table exists
        logger.info("Testing crawler status table...")
        cursor.execute("""
            SELECT COUNT(*) FROM crawler_status
        """)
        count = cursor.fetchone()[0]
        logger.info(f"Found {count} crawler records in table")
        
        # Test 2: Update some test status
        test_crawlers = [
            ("twitter", "online", 150, None),
            ("reddit", "online", 89, None),
            ("news", "online", 45, None),
            ("crypto", "online", 200, None),
            ("dexpaprika", "stale", 12, "Rate limit exceeded"),
            ("dexscreener", "offline", 0, "Connection timeout"),
            ("migration_service", "online", 5, None)
        ]
        
        for crawler_name, status, items, error in test_crawlers:
            cursor.execute(
                "SELECT update_crawler_status(%s, %s, %s, %s)",
                (crawler_name, status, items, error)
            )
            logger.info(f"Updated {crawler_name} to {status}")
        
        # Test 3: Update counts
        cursor.execute("SELECT update_crawler_counts()")
        logger.info("Updated crawler counts")
        
        # Test 4: Verify the data
        cursor.execute("""
            SELECT 
                crawler_name,
                status,
                last_run_at,
                items_collected,
                items_collected_24h,
                items_collected_1h,
                error_message
            FROM crawler_status
            ORDER BY crawler_name
        """)
        
        rows = cursor.fetchall()
        logger.info("Current crawler status:")
        for row in rows:
            crawler_name, status, last_run, total_items, items_24h, items_1h, error = row
            logger.info(f"  {crawler_name}: {status} (items: {total_items}, 24h: {items_24h}, 1h: {items_1h})")
            if error:
                logger.info(f"    Error: {error}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Crawler status table test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing crawler status: {e}")
        return False

if __name__ == "__main__":
    test_crawler_status() 