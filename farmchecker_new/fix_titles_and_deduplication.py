#!/usr/bin/env python3
"""
Fix Titles and Deduplication Script
==================================

This script addresses two remaining issues:
1. Fix title extraction to show actual tweet text instead of "Crypto Update"
2. Implement deduplication to remove duplicate entries

Author: FarmChecker.xyz Development Team
Version: 1.0.0
"""

import json
import psycopg2
import logging
import hashlib
from datetime import datetime
from collections import defaultdict

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

def extract_tweet_title(content, raw_data):
    """Extract a proper title from tweet content or raw data"""
    try:
        # First try to use the cleaned content
        if content and len(content) > 10:
            # Create a title from the first sentence or first 100 characters
            title = content.split('.')[0] if '.' in content else content[:100]
            title = title.strip()
            
            # Remove common prefixes and clean up
            title = title.replace('RT @', '').replace('@', '')
            title = title.replace('https://', '').replace('http://', '')
            
            # Limit length for title
            if len(title) > 150:
                title = title[:147] + "..."
                
            return title
        
        # Fallback to raw_data if content is not available
        if raw_data:
            if isinstance(raw_data, str):
                data = json.loads(raw_data)
            else:
                data = raw_data
            
            # Extract text from raw_data
            tweet_text = (
                data.get("text") or 
                data.get("content") or 
                data.get("tweet_text") or
                data.get("message") or
                ""
            )
            
            if tweet_text:
                title = tweet_text.split('.')[0] if '.' in tweet_text else tweet_text[:100]
                title = title.strip()
                
                # Clean up title
                title = title.replace('RT @', '').replace('@', '')
                title = title.replace('https://', '').replace('http://', '')
                
                if len(title) > 150:
                    title = title[:147] + "..."
                    
                return title
        
        return "Tweet"
        
    except Exception as e:
        logger.error(f"Error extracting title: {e}")
        return "Tweet"

def create_content_hash(content, author, published_at):
    """Create a hash to identify duplicate content"""
    try:
        # Create a hash based on content, author, and published time
        hash_string = f"{content}_{author}_{published_at}"
        return hashlib.md5(hash_string.encode('utf-8')).hexdigest()
    except Exception as e:
        logger.error(f"Error creating content hash: {e}")
        return None

def fix_titles():
    """Fix titles to show actual tweet content instead of 'Crypto Update'"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get all Twitter content items that need title fixing
        cursor.execute("""
            SELECT ci.id, ci.title, ci.content, ci.raw_data, ci.author, ci.published_at
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name = 'twitter'
            AND (ci.title = 'Crypto Update' OR ci.title IS NULL OR ci.title = '')
        """)
        
        rows = cursor.fetchall()
        logger.info(f"Found {len(rows)} Twitter content items that need title fixing")
        
        fixed_count = 0
        for row in rows:
            content_id, title, content, raw_data, author, published_at = row
            
            try:
                # Extract proper title
                new_title = extract_tweet_title(content, raw_data)
                
                if new_title and new_title != title:
                    # Update the title
                    cursor.execute("""
                        UPDATE content_items 
                        SET title = %s 
                        WHERE id = %s
                    """, (new_title, content_id))
                    
                    fixed_count += 1
                    logger.info(f"Fixed title for ID {content_id}: {new_title[:50]}...")
                    
            except Exception as e:
                logger.error(f"Error fixing title for ID {content_id}: {e}")
                continue
        
        conn.commit()
        logger.info(f"Fixed {fixed_count} titles")
        
    except Exception as e:
        logger.error(f"Error fixing titles: {e}")
        conn.rollback()
    finally:
        conn.close()

def implement_deduplication():
    """Remove duplicate content items based on content hash"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get all Twitter content items
        cursor.execute("""
            SELECT ci.id, ci.content, ci.author, ci.published_at, ci.created_at
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name = 'twitter'
            ORDER BY ci.created_at ASC
        """)
        
        rows = cursor.fetchall()
        logger.info(f"Analyzing {len(rows)} Twitter content items for duplicates")
        
        # Group by content hash
        content_groups = defaultdict(list)
        for row in rows:
            content_id, content, author, published_at, created_at = row
            
            if content:
                content_hash = create_content_hash(content, author, published_at)
                if content_hash:
                    content_groups[content_hash].append({
                        'id': content_id,
                        'content': content,
                        'author': author,
                        'published_at': published_at,
                        'created_at': created_at
                    })
        
        # Find and remove duplicates
        duplicates_removed = 0
        for content_hash, items in content_groups.items():
            if len(items) > 1:
                # Sort by creation time, keep the oldest (first created)
                items.sort(key=lambda x: x['created_at'])
                
                # Keep the first item, remove the rest
                items_to_remove = items[1:]
                
                for item in items_to_remove:
                    cursor.execute("DELETE FROM content_items WHERE id = %s", (item['id'],))
                    duplicates_removed += 1
                    logger.info(f"Removed duplicate ID {item['id']} (content: {item['content'][:50]}...)")
        
        conn.commit()
        logger.info(f"Removed {duplicates_removed} duplicate content items")
        
        # Get final count
        cursor.execute("""
            SELECT COUNT(*) 
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name = 'twitter'
        """)
        
        final_count = cursor.fetchone()[0]
        logger.info(f"Final Twitter content count: {final_count}")
        
    except Exception as e:
        logger.error(f"Error implementing deduplication: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_fixes():
    """Verify that titles and deduplication worked correctly"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check title fixes
        cursor.execute("""
            SELECT ci.id, ci.title, ci.content, ci.author
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name = 'twitter'
            ORDER BY ci.created_at DESC
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        logger.info("Verifying title fixes:")
        
        for row in rows:
            content_id, title, content, author = row
            logger.info(f"ID {content_id}: Title: {title[:50]}... | Content: {content[:50]}...")
        
        # Check for remaining duplicates
        cursor.execute("""
            SELECT ci.content, ci.author, ci.published_at, COUNT(*) as count
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name = 'twitter'
            GROUP BY ci.content, ci.author, ci.published_at
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 5
        """)
        
        duplicate_groups = cursor.fetchall()
        if duplicate_groups:
            logger.warning(f"Found {len(duplicate_groups)} remaining duplicate groups")
            for group in duplicate_groups:
                content, author, published_at, count = group
                logger.warning(f"  {count} duplicates: {content[:50]}... by {author}")
        else:
            logger.info("No remaining duplicates found")
        
    except Exception as e:
        logger.error(f"Error verifying fixes: {e}")
    finally:
        conn.close()

def main():
    """Main function to fix titles and implement deduplication"""
    logger.info("Starting title fixes and deduplication...")
    
    # Step 1: Fix titles
    logger.info("Step 1: Fixing titles...")
    fix_titles()
    
    # Step 2: Implement deduplication
    logger.info("Step 2: Implementing deduplication...")
    implement_deduplication()
    
    # Step 3: Verify fixes
    logger.info("Step 3: Verifying fixes...")
    verify_fixes()
    
    logger.info("Title fixes and deduplication completed!")

if __name__ == "__main__":
    main() 