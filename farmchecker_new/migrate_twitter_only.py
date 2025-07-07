#!/usr/bin/env python3
"""
Migrate Twitter data from GCS to tweets table only
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

def migrate_twitter_data():
    """Migrate Twitter data from GCS to tweets table"""
    logger.info("🔄 Starting Twitter data migration...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    client, bucket = get_gcs_client()
    if not bucket:
        return False
    
    try:
        cursor = conn.cursor()
        
        # List all Twitter files in GCS
        blobs = list(bucket.list_blobs(prefix="twitter_data/"))
        logger.info(f"Found {len(blobs)} Twitter files to migrate")
        
        total_migrated = 0
        
        for blob in blobs:
            if not blob.name.endswith('.json'):
                continue
                
            try:
                # Download and parse JSON
                content = blob.download_as_text()
                data = json.loads(content)
                
                # Extract tweets from the data
                tweets = data.get('tweets', [])
                if not tweets:
                    tweets = data.get('data', [])
                
                logger.info(f"Processing {blob.name} with {len(tweets)} tweets")
                
                file_migrated = 0
                
                for tweet in tweets:
                    try:
                        # Extract engagement data
                        engagement = tweet.get('engagement', {})
                        
                        cursor.execute("""
                            INSERT INTO tweets (
                                tweet_id, author_username, author_display_name, author_verified,
                                author_followers_count, content, url, published_at, collected_at,
                                likes_count, retweets_count, replies_count, views_count,
                                engagement_score, virality_score, sentiment_score,
                                viral_keywords, category, urgency, raw_data
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            ) ON CONFLICT (tweet_id) DO NOTHING
                        """, (
                            tweet.get('id') or tweet.get('tweet_id'),
                            tweet.get('username') or tweet.get('author_username'),
                            tweet.get('display_name') or tweet.get('author_display_name'),
                            tweet.get('verified', False),
                            tweet.get('followers_count', 0),
                            tweet.get('text') or tweet.get('content'),
                            tweet.get('url'),
                            tweet.get('published_at') or tweet.get('created_at'),
                            datetime.now(),
                            engagement.get('likes', 0),
                            engagement.get('retweets', 0),
                            engagement.get('replies', 0),
                            engagement.get('views', 0),
                            tweet.get('engagement_score', 0),
                            tweet.get('virality_score', 0),
                            tweet.get('sentiment_score', 0),
                            json.dumps(tweet.get('viral_keywords', [])),
                            tweet.get('category', 'general'),
                            tweet.get('urgency', 'low'),
                            json.dumps(tweet)
                        ))
                        
                        file_migrated += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing tweet: {e}")
                        # Rollback the current transaction and continue
                        conn.rollback()
                        continue
                
                # Commit after each file to avoid long transactions
                conn.commit()
                total_migrated += file_migrated
                logger.info(f"✅ Migrated {blob.name} ({file_migrated} tweets)")
                
            except Exception as e:
                logger.error(f"Error processing file {blob.name}: {e}")
                conn.rollback()
                continue
        
        logger.info(f"🎉 Twitter migration complete! Migrated {total_migrated} tweets")
        return True
        
    except Exception as e:
        logger.error(f"❌ Twitter migration failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_twitter_data()
    if success:
        logger.info("✅ Twitter migration completed successfully!")
    else:
        logger.error("❌ Twitter migration failed!") 