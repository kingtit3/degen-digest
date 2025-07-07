#!/usr/bin/env python3
"""
Regular Reddit migration script - can be scheduled to run automatically
Migrates Reddit data from GCS to PostgreSQL redditpost table
"""

import json
import psycopg2
import subprocess
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# PostgreSQL connection
PG_CONFIG = {
    "host": "34.9.71.174",
    "database": "degen_digest",
    "user": "postgres",
    "password": "DegenDigest2024!",
    "port": "5432"
}

def get_reddit_data_from_gcs():
    """Get Reddit data from GCS latest file"""
    try:
        # Get the latest reddit data from GCS
        cmd = ["gsutil", "cat", "gs://degen-digest-data/reddit_data/reddit_latest.json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Error getting GCS data: {result.stderr}")
            return []
        
        data = json.loads(result.stdout)
        return data.get("posts", [])
        
    except Exception as e:
        logger.error(f"Error reading GCS data: {e}")
        return []

def migrate_to_postgres(posts):
    """Migrate Reddit posts to PostgreSQL"""
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Don't clear existing data, just add new ones
        migrated_count = 0
        
        for i, post in enumerate(posts):
            # Extract post_id from URL
            post_id = post.get("link", "").split("/comments/")[-1].split("/")[0] if "/comments/" in post.get("link", "") else f"post_{i}"
            
            # Parse published date
            published_str = post.get("published", "")
            try:
                if published_str:
                    # Handle ISO format with timezone
                    if "+" in published_str:
                        published_str = published_str.split("+")[0]
                    created_at = datetime.fromisoformat(published_str.replace("Z", ""))
                else:
                    created_at = datetime.now()
            except:
                created_at = datetime.now()
            
            # Check if post already exists
            cursor.execute("SELECT id FROM redditpost WHERE post_id = %s", (post_id,))
            if cursor.fetchone():
                continue  # Skip if already exists
            
            cursor.execute("""
                INSERT INTO redditpost (
                    post_id, title, author, subreddit, score, num_comments, 
                    created_at, link, scraped_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                post_id,
                post.get("title", ""),
                post.get("author", "Anonymous"),
                post.get("subreddit", ""),
                post.get("score", 0),
                post.get("num_comments", 0),
                created_at,
                post.get("link", ""),
                datetime.now()
            ))
            migrated_count += 1
        
        conn.commit()
        logger.info(f"Successfully migrated {migrated_count} new Reddit posts to PostgreSQL")
        
        # Clean up old posts (older than 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        cursor.execute("DELETE FROM redditpost WHERE created_at < %s", (cutoff_date,))
        deleted_count = cursor.rowcount
        conn.commit()
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old Reddit posts")
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM redditpost")
        total_count = cursor.fetchone()[0]
        logger.info(f"Total Reddit posts in PostgreSQL: {total_count}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error during migration: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    logger.info("Starting regular Reddit migration from GCS to PostgreSQL...")
    
    # Get data from GCS
    logger.info("Fetching Reddit data from GCS...")
    posts = get_reddit_data_from_gcs()
    
    if not posts:
        logger.warning("No Reddit posts found in GCS")
        return
    
    logger.info(f"Found {len(posts)} Reddit posts to process")
    
    # Migrate to PostgreSQL
    logger.info("Migrating to PostgreSQL...")
    migrate_to_postgres(posts)
    
    logger.info("Regular Reddit migration completed successfully!")

if __name__ == "__main__":
    main() 