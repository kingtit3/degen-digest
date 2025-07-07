#!/usr/bin/env python3
"""
Migrate Reddit data from GCS to reddit_posts table only
"""

import json
import logging
import os
from datetime import datetime
from google.cloud import storage
import psycopg2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "34.9.71.174"),
            database=os.getenv("DB_NAME", "degen_digest"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "DegenDigest2024!"),
            port=os.getenv("DB_PORT", "5432")
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def get_gcs_client():
    """Create GCS client"""
    try:
        client = storage.Client()
        bucket = client.bucket("degen-digest-data")
        return client, bucket
    except Exception as e:
        logger.error(f"GCS connection failed: {e}")
        return None, None

def migrate_reddit_data():
    """Migrate Reddit data from GCS to reddit_posts table"""
    logger.info("🔄 Starting Reddit data migration...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    client, bucket = get_gcs_client()
    if not bucket:
        return False
    
    try:
        cursor = conn.cursor()
        
        # List all Reddit files in GCS
        blobs = list(bucket.list_blobs(prefix="reddit_data/"))
        logger.info(f"Found {len(blobs)} Reddit files to migrate")
        
        total_migrated = 0
        
        for blob in blobs:
            if not blob.name.endswith('.json'):
                continue
                
            try:
                # Download and parse JSON
                content = blob.download_as_text()
                data = json.loads(content)
                
                # Extract posts from the data - handle different structures
                posts = data.get('posts', [])
                if not posts:
                    posts = data.get('data', [])
                if not posts and isinstance(data, list):
                    posts = data
                
                logger.info(f"Processing {blob.name} with {len(posts)} posts")
                
                file_migrated = 0
                
                for post in posts:
                    try:
                        # Skip posts without ID
                        post_id = post.get('id') or post.get('post_id')
                        if not post_id:
                            logger.warning(f"Skipping post without ID: {post.get('title', 'Unknown')}")
                            continue
                        
                        # Handle missing username with default value
                        username = post.get('username') or post.get('author_username') or 'unknown_user'
                        
                        cursor.execute("""
                            INSERT INTO reddit_posts (
                                post_id, subreddit, author_username, title, content, url,
                                is_original_content, published_at, collected_at,
                                upvotes, downvotes, comments_count, score,
                                engagement_score, virality_score, sentiment_score,
                                viral_keywords, category, urgency, raw_data
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            ) ON CONFLICT (post_id) DO NOTHING
                        """, (
                            post_id,
                            post.get('subreddit'),
                            username,
                            post.get('title'),
                            post.get('text') or post.get('content'),
                            post.get('url'),
                            post.get('is_original_content', False),
                            post.get('published_at') or post.get('created_at'),
                            datetime.now(),
                            post.get('upvotes', 0),
                            post.get('downvotes', 0),
                            post.get('comments_count', 0),
                            post.get('score', 0),
                            post.get('engagement_score', 0),
                            post.get('virality_score', 0),
                            post.get('sentiment_score', 0),
                            json.dumps(post.get('viral_keywords', [])),
                            post.get('category', 'general'),
                            post.get('urgency', 'low'),
                            json.dumps(post)
                        ))
                        
                        file_migrated += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing post: {e}")
                        # Rollback the current transaction and continue
                        conn.rollback()
                        continue
                
                # Commit after each file to avoid long transactions
                conn.commit()
                total_migrated += file_migrated
                logger.info(f"✅ Migrated {blob.name} ({file_migrated} posts)")
                
            except Exception as e:
                logger.error(f"Error processing file {blob.name}: {e}")
                conn.rollback()
                continue
        
        logger.info(f"🎉 Reddit migration complete! Migrated {total_migrated} posts")
        return True
        
    except Exception as e:
        logger.error(f"❌ Reddit migration failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_reddit_data()
    if success:
        logger.info("✅ Reddit migration completed successfully!")
    else:
        logger.error("❌ Reddit migration failed!") 