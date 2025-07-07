#!/usr/bin/env python3
"""
Setup script for crawler status tracking table
"""

import os
import psycopg2
import logging

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

def setup_crawler_status_table():
    """Create the crawler status table and functions"""
    try:
        # Read the SQL file
        with open('create_crawler_status_table.sql', 'r') as f:
            sql_script = f.read()
        
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Execute the SQL script
        logger.info("Creating crawler status table and functions...")
        cursor.execute(sql_script)
        
        # Commit the changes
        conn.commit()
        
        # Verify the table was created
        cursor.execute("""
            SELECT crawler_name, status, last_run_at 
            FROM crawler_status 
            ORDER BY crawler_name
        """)
        
        rows = cursor.fetchall()
        logger.info(f"Successfully created crawler status table with {len(rows)} crawlers:")
        for row in rows:
            logger.info(f"  - {row[0]}: {row[1]} (last run: {row[2]})")
        
        cursor.close()
        conn.close()
        
        logger.info("Crawler status table setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up crawler status table: {e}")
        return False

if __name__ == "__main__":
    setup_crawler_status_table() 