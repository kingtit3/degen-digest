#!/usr/bin/env python3
"""
Migration script to move data from GCS buckets to dedicated tables
This script handles the migration from the old bucket structure to new dedicated tables
"""

import json
import logging
import os
import psycopg2
from datetime import datetime
from google.cloud import storage
from typing import Dict, List, Any

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

# GCS configuration
GCS_BUCKET_NAME = "degen-digest-data"

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def get_gcs_client():
    """Get GCS client"""
    try:
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        return client, bucket
    except Exception as e:
        logger.error(f"GCS client error: {e}")
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
                            post.get('username') or post.get('author_username') or 'unknown_user',
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

def migrate_crypto_data():
    """Migrate crypto data from GCS to crypto_tokens table"""
    logger.info("🔄 Starting crypto data migration...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    client, bucket = get_gcs_client()
    if not bucket:
        return False
    
    try:
        cursor = conn.cursor()
        
        # List all crypto files in GCS
        blobs = list(bucket.list_blobs(prefix="crypto_data/"))
        logger.info(f"Found {len(blobs)} crypto files to migrate")
        
        total_migrated = 0
        
        for blob in blobs:
            if not blob.name.endswith('.json'):
                continue
                
            try:
                # Download and parse JSON
                content = blob.download_as_text()
                data = json.loads(content)
                
                # Extract tokens from the data - handle different structures
                tokens = data.get('tokens', [])
                if not tokens:
                    tokens = data.get('data', [])
                if not tokens and isinstance(data, list):
                    tokens = data
                if not tokens and isinstance(data, dict):
                    # Try to find any array that might contain tokens
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            if isinstance(value[0], dict) and 'symbol' in value[0]:
                                tokens = value
                                break
                
                logger.info(f"Processing {blob.name} with {len(tokens)} tokens")
                
                for token in tokens:
                    try:
                        cursor.execute("""
                            INSERT INTO crypto_tokens (
                                symbol, name, network, contract_address, market_cap,
                                price_usd, volume_24h, price_change_24h,
                                first_seen_at, last_updated_at
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            ) ON CONFLICT (symbol) DO UPDATE SET
                                price_usd = EXCLUDED.price_usd,
                                market_cap = EXCLUDED.market_cap,
                                volume_24h = EXCLUDED.volume_24h,
                                price_change_24h = EXCLUDED.price_change_24h,
                                last_updated_at = CURRENT_TIMESTAMP
                        """, (
                            token.get('symbol'),
                            token.get('name'),
                            token.get('network'),
                            token.get('contract_address'),
                            token.get('market_cap'),
                            token.get('price_usd') or token.get('price'),
                            token.get('volume_24h'),
                            token.get('price_change_24h'),
                            datetime.now(),
                            datetime.now()
                        ))
                        
                        total_migrated += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing token: {e}")
                        continue
                
                conn.commit()
                logger.info(f"✅ Migrated {blob.name}")
                
            except Exception as e:
                logger.error(f"Error processing file {blob.name}: {e}")
                continue
        
        logger.info(f"🎉 Crypto migration complete! Migrated {total_migrated} tokens")
        return True
        
    except Exception as e:
        logger.error(f"❌ Crypto migration failed: {e}")
        return False
    finally:
        conn.close()

def migrate_dex_data():
    """Migrate DEX data from GCS to dex_pairs table"""
    logger.info("🔄 Starting DEX data migration...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    client, bucket = get_gcs_client()
    if not bucket:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Migrate DexScreener data
        dexscreener_blobs = list(bucket.list_blobs(prefix="dexscreener_data/"))
        logger.info(f"Found {len(dexscreener_blobs)} DexScreener files to migrate")
        
        total_migrated = 0
        
        # Process DexScreener files
        for blob in dexscreener_blobs:
            if not blob.name.endswith('.json'):
                continue
                
            try:
                content = blob.download_as_text()
                data = json.loads(content)
                
                pairs = data.get('pairs', [])
                if not pairs:
                    pairs = data.get('data', [])
                
                logger.info(f"Processing {blob.name} with {len(pairs)} pairs")
                
                for pair in pairs:
                    try:
                        cursor.execute("""
                            INSERT INTO dex_pairs (
                                pair_id, base_token_symbol, base_token_name, base_token_address,
                                quote_token_symbol, quote_token_name, quote_token_address,
                                dex_name, chain_name, price_usd, price_change_24h,
                                volume_24h, liquidity_usd, market_cap, txns_24h, fdv,
                                source, published_at, collected_at, raw_data
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            ) ON CONFLICT (pair_id) DO UPDATE SET
                                price_usd = EXCLUDED.price_usd,
                                price_change_24h = EXCLUDED.price_change_24h,
                                volume_24h = EXCLUDED.volume_24h,
                                liquidity_usd = EXCLUDED.liquidity_usd,
                                market_cap = EXCLUDED.market_cap,
                                txns_24h = EXCLUDED.txns_24h,
                                fdv = EXCLUDED.fdv,
                                last_updated_at = CURRENT_TIMESTAMP
                        """, (
                            pair.get('pair_id') or pair.get('id'),
                            pair.get('base_token', {}).get('symbol'),
                            pair.get('base_token', {}).get('name'),
                            pair.get('base_token', {}).get('address'),
                            pair.get('quote_token', {}).get('symbol'),
                            pair.get('quote_token', {}).get('name'),
                            pair.get('quote_token', {}).get('address'),
                            pair.get('dex_name'),
                            pair.get('chain_name'),
                            pair.get('price_usd') or pair.get('price'),
                            pair.get('price_change_24h'),
                            pair.get('volume_24h'),
                            pair.get('liquidity_usd'),
                            pair.get('market_cap'),
                            pair.get('txns_24h'),
                            pair.get('fdv'),
                            'dexscreener',
                            pair.get('published_at'),
                            datetime.now(),
                            json.dumps(pair)
                        ))
                        
                        total_migrated += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing pair: {e}")
                        continue
                
                conn.commit()
                logger.info(f"✅ Migrated {blob.name}")
                
            except Exception as e:
                logger.error(f"Error processing file {blob.name}: {e}")
                continue
        
        # Process DexPaprika files (similar structure)
        dexpaprika_blobs = list(bucket.list_blobs(prefix="dexpaprika_data/"))
        logger.info(f"Found {len(dexpaprika_blobs)} DexPaprika files to migrate")
        
        for blob in dexpaprika_blobs:
            if not blob.name.endswith('.json'):
                continue
                
            try:
                content = blob.download_as_text()
                data = json.loads(content)
                
                pairs = data.get('pairs', [])
                if not pairs:
                    pairs = data.get('data', [])
                
                logger.info(f"Processing {blob.name} with {len(pairs)} pairs")
                
                for pair in pairs:
                    try:
                        cursor.execute("""
                            INSERT INTO dex_pairs (
                                pair_id, base_token_symbol, base_token_name, base_token_address,
                                quote_token_symbol, quote_token_name, quote_token_address,
                                dex_name, chain_name, price_usd, price_change_24h,
                                volume_24h, liquidity_usd, market_cap, txns_24h, fdv,
                                source, published_at, collected_at, raw_data
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            ) ON CONFLICT (pair_id) DO UPDATE SET
                                price_usd = EXCLUDED.price_usd,
                                price_change_24h = EXCLUDED.price_change_24h,
                                volume_24h = EXCLUDED.volume_24h,
                                liquidity_usd = EXCLUDED.liquidity_usd,
                                market_cap = EXCLUDED.market_cap,
                                txns_24h = EXCLUDED.txns_24h,
                                fdv = EXCLUDED.fdv,
                                last_updated_at = CURRENT_TIMESTAMP
                        """, (
                            pair.get('pair_id') or pair.get('id'),
                            pair.get('base_token', {}).get('symbol'),
                            pair.get('base_token', {}).get('name'),
                            pair.get('base_token', {}).get('address'),
                            pair.get('quote_token', {}).get('symbol'),
                            pair.get('quote_token', {}).get('name'),
                            pair.get('quote_token', {}).get('address'),
                            pair.get('dex_name'),
                            pair.get('chain_name'),
                            pair.get('price_usd') or pair.get('price'),
                            pair.get('price_change_24h'),
                            pair.get('volume_24h'),
                            pair.get('liquidity_usd'),
                            pair.get('market_cap'),
                            pair.get('txns_24h'),
                            pair.get('fdv'),
                            'dexpaprika',
                            pair.get('published_at'),
                            datetime.now(),
                            json.dumps(pair)
                        ))
                        
                        total_migrated += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing pair: {e}")
                        continue
                
                conn.commit()
                logger.info(f"✅ Migrated {blob.name}")
                
            except Exception as e:
                logger.error(f"Error processing file {blob.name}: {e}")
                continue
        
        logger.info(f"🎉 DEX migration complete! Migrated {total_migrated} pairs")
        return True
        
    except Exception as e:
        logger.error(f"❌ DEX migration failed: {e}")
        return False
    finally:
        conn.close()

def update_crawler_counts():
    """Update crawler status counts from dedicated tables"""
    logger.info("🔄 Updating crawler counts...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Execute the function to update counts
        cursor.execute("SELECT update_dedicated_crawler_counts()")
        
        conn.commit()
        logger.info("✅ Crawler counts updated")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update crawler counts: {e}")
        return False
    finally:
        conn.close()

def main():
    """Run the complete migration"""
    logger.info("🚀 Starting migration to dedicated tables...")
    
    # Skip table creation since they already exist
    logger.info("📋 Tables already exist, proceeding with data migration...")
    
    # Run migrations
    success_count = 0
    
    if migrate_twitter_data():
        success_count += 1
    
    if migrate_reddit_data():
        success_count += 1
    
    if migrate_crypto_data():
        success_count += 1
    
    if migrate_dex_data():
        success_count += 1
    
    # Update crawler counts
    update_crawler_counts()
    
    logger.info(f"🎉 Migration complete! {success_count}/4 data sources migrated successfully")

if __name__ == "__main__":
    main() 