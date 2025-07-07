#!/usr/bin/env python3
"""
Fix Content Issue Script
=======================

This script diagnoses and fixes the issue where raw data is stored in the content column
instead of cleaned, processed text. The web should be pulling clean data from the database,
not raw data that needs processing on the fly.
"""

import json
import psycopg2
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "host": "34.9.71.174",
    "database": "degen_digest",
    "user": "postgres",
    "password": "DegenDigest2024!",
    "port": "5432",
}

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def clean_tweet_content(raw_data):
    """Extract clean tweet text from raw data"""
    try:
        if not raw_data:
            return ""
        
        # Parse JSON if it's a string
        if isinstance(raw_data, str):
            data = json.loads(raw_data)
        else:
            data = raw_data
        
        # Extract tweet text from various possible locations
        tweet_text = (
            data.get("text") or 
            data.get("content") or 
            data.get("tweet_text") or
            data.get("message") or
            ""
        )
        
        # Clean up the text
        if tweet_text:
            # Remove escape characters
            tweet_text = tweet_text.replace('\\n', ' ').replace('\\t', ' ')
            tweet_text = tweet_text.replace('\\"', '"').replace("\\'", "'")
            tweet_text = tweet_text.replace('\u2014', '-')  # Handle em dash
            tweet_text = tweet_text.strip()
            
        return tweet_text
        
    except Exception as e:
        logger.error(f"Error cleaning tweet content: {e}")
        return ""

def diagnose_content_issue():
    """Diagnose the content issue in the database"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check Twitter content items
        cursor.execute("""
            SELECT ci.id, ci.title, ci.content, ci.raw_data, ci.author
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name = 'twitter'
            ORDER BY ci.created_at DESC
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        logger.info(f"Found {len(rows)} Twitter content items to analyze")
        
        raw_content_count = 0
        clean_content_count = 0
        
        for row in rows:
            content_id, title, content, raw_data, author = row
            
            # Check if content looks like raw data
            is_raw_data = (
                content and 
                (content.startswith('{') or 
                 content.startswith("'") or 
                 "'text':" in str(content) or
                 '"text":' in str(content))
            )
            
            if is_raw_data:
                raw_content_count += 1
                logger.info(f"ID {content_id}: Content contains raw data")
                
                # Extract clean text from raw_data
                clean_text = clean_tweet_content(raw_data)
                if clean_text:
                    logger.info(f"  Clean text: {clean_text[:100]}...")
                else:
                    logger.info(f"  Could not extract clean text")
            else:
                clean_content_count += 1
                logger.info(f"ID {content_id}: Content appears clean")
        
        logger.info(f"Summary: {raw_content_count} items with raw data, {clean_content_count} items with clean content")
        
        return raw_content_count > 0
        
    except Exception as e:
        logger.error(f"Error diagnosing content: {e}")
        return False
    finally:
        conn.close()

def fix_content_issue():
    """Fix the content issue by updating the content column with clean text"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get all Twitter content items that need fixing
        cursor.execute("""
            SELECT ci.id, ci.content, ci.raw_data
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name = 'twitter'
            AND (ci.content LIKE '{%' OR ci.content LIKE '%text%')
        """)
        
        rows = cursor.fetchall()
        logger.info(f"Found {len(rows)} Twitter content items to fix")
        
        fixed_count = 0
        for row in rows:
            content_id, content, raw_data = row
            
            try:
                # Extract clean text from raw_data
                clean_text = clean_tweet_content(raw_data)
                
                if clean_text:
                    # Update the content column with clean text
                    cursor.execute("""
                        UPDATE content_items 
                        SET content = %s 
                        WHERE id = %s
                    """, (clean_text, content_id))
                    
                    fixed_count += 1
                    logger.info(f"Fixed content for ID {content_id}: {clean_text[:50]}...")
                else:
                    logger.warning(f"Could not extract clean text for ID {content_id}")
                    
            except Exception as e:
                logger.error(f"Error fixing content for ID {content_id}: {e}")
                continue
        
        conn.commit()
        logger.info(f"Fixed {fixed_count} content items")
        
    except Exception as e:
        logger.error(f"Error fixing content: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_fix():
    """Verify that the content has been fixed"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check a few items to verify they're clean
        cursor.execute("""
            SELECT ci.id, ci.title, ci.content, ci.author
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name = 'twitter'
            ORDER BY ci.created_at DESC
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        logger.info("Verifying content fix:")
        
        for row in rows:
            content_id, title, content, author = row
            logger.info(f"ID {content_id}: {content[:100]}...")
        
    except Exception as e:
        logger.error(f"Error verifying fix: {e}")
    finally:
        conn.close()

def main():
    """Main function to diagnose and fix the content issue"""
    logger.info("Starting content issue diagnosis and fix...")
    
    # Step 1: Diagnose the issue
    logger.info("Step 1: Diagnosing content issue...")
    has_issue = diagnose_content_issue()
    
    if has_issue:
        logger.info("Content issue detected. Proceeding with fix...")
        
        # Step 2: Fix the issue
        logger.info("Step 2: Fixing content issue...")
        fix_content_issue()
        
        # Step 3: Verify the fix
        logger.info("Step 3: Verifying fix...")
        verify_fix()
        
        logger.info("Content issue fix completed!")
    else:
        logger.info("No content issue detected.")

if __name__ == "__main__":
    main() 