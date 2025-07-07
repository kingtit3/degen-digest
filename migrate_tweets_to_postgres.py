#!/usr/bin/env python3
"""
Migrate tweet data from VM SQLite to PostgreSQL
"""

import sqlite3
import psycopg2
import os
from datetime import datetime

# PostgreSQL connection
PG_CONFIG = {
    "host": "34.9.71.174",
    "database": "degen_digest",
    "user": "postgres",
    "password": "DegenDigest2024!",
    "port": "5432"
}

def get_sqlite_data():
    """Get tweet data from VM SQLite database"""
    # Connect to VM and get data
    import subprocess
    
    cmd = [
        "gcloud", "compute", "ssh", "twitter-crawler-vm", 
        "--zone=us-central1-a", 
        "--command=sqlite3 /home/king/DegenDigest/output/degen_digest.db 'SELECT * FROM tweet ORDER BY created_at DESC;'"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error getting SQLite data: {result.stderr}")
        return []
    
    lines = result.stdout.strip().split('\n')
    tweets = []
    
    for line in lines:
        if line.strip():
            parts = line.split('|')
            if len(parts) >= 14:
                tweet = {
                    'id': int(parts[0]),
                    'tweet_id': parts[1],
                    'full_text': parts[2],
                    'user_screen_name': parts[3],
                    'user_followers_count': int(parts[4]) if parts[4] else 0,
                    'user_verified': parts[5] == '1',
                    'like_count': int(parts[6]) if parts[6] else 0,
                    'retweet_count': int(parts[7]) if parts[7] else 0,
                    'reply_count': int(parts[8]) if parts[8] else 0,
                    'view_count': int(parts[9]) if parts[9] else None,
                    'quote_count': int(parts[10]) if parts[10] else None,
                    'bookmark_count': int(parts[11]) if parts[11] else None,
                    'created_at': parts[12] if parts[12] else None,
                    'scraped_at': parts[13] if parts[13] else None
                }
                tweets.append(tweet)
    
    return tweets

def migrate_to_postgres(tweets):
    """Migrate tweets to PostgreSQL"""
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Clear existing data
        cursor.execute("DELETE FROM tweet")
        print(f"Cleared existing tweet data")
        
        # Insert new data
        for tweet in tweets:
            cursor.execute("""
                INSERT INTO tweet (
                    tweet_id, full_text, user_screen_name, user_followers_count,
                    user_verified, like_count, retweet_count, reply_count,
                    view_count, quote_count, bookmark_count, created_at, scraped_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tweet_id) DO NOTHING
            """, (
                tweet['tweet_id'], tweet['full_text'], tweet['user_screen_name'],
                tweet['user_followers_count'], tweet['user_verified'],
                tweet['like_count'], tweet['retweet_count'], tweet['reply_count'],
                tweet['view_count'], tweet['quote_count'], tweet['bookmark_count'],
                tweet['created_at'], tweet['scraped_at']
            ))
        
        conn.commit()
        print(f"Successfully migrated {len(tweets)} tweets to PostgreSQL")
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM tweet")
        count = cursor.fetchone()[0]
        print(f"Total tweets in PostgreSQL: {count}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    print("Starting tweet migration from SQLite to PostgreSQL...")
    
    # Get data from SQLite
    print("Fetching tweet data from VM SQLite database...")
    tweets = get_sqlite_data()
    
    if not tweets:
        print("No tweets found in SQLite database")
        return
    
    print(f"Found {len(tweets)} tweets to migrate")
    
    # Show sample data
    print("\nSample tweets:")
    for i, tweet in enumerate(tweets[:3]):
        print(f"{i+1}. {tweet['user_screen_name']}: {tweet['full_text'][:100]}...")
    
    # Migrate to PostgreSQL
    print("\nMigrating to PostgreSQL...")
    migrate_to_postgres(tweets)
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    main() 