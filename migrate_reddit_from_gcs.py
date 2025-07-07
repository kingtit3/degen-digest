#!/usr/bin/env python3
"""
Migrate Reddit data from GCS JSON files to PostgreSQL redditpost table
"""

import json
import psycopg2
import subprocess
from datetime import datetime

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
            print(f"Error getting GCS data: {result.stderr}")
            return []
        
        data = json.loads(result.stdout)
        return data.get("posts", [])
        
    except Exception as e:
        print(f"Error reading GCS data: {e}")
        return []

def migrate_to_postgres(posts):
    """Migrate Reddit posts to PostgreSQL"""
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Clear existing data
        cursor.execute("DELETE FROM redditpost")
        print(f"Cleared existing redditpost data")
        
        # Insert new data
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
            
            cursor.execute("""
                INSERT INTO redditpost (
                    post_id, title, author, subreddit, score, num_comments, 
                    created_at, link, scraped_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (post_id) DO NOTHING
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
        
        conn.commit()
        print(f"Successfully migrated {len(posts)} Reddit posts to PostgreSQL")
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM redditpost")
        count = cursor.fetchone()[0]
        print(f"Total Reddit posts in PostgreSQL: {count}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    print("Starting Reddit migration from GCS to PostgreSQL...")
    
    # Get data from GCS
    print("Fetching Reddit data from GCS...")
    posts = get_reddit_data_from_gcs()
    
    if not posts:
        print("No Reddit posts found in GCS")
        return
    
    print(f"Found {len(posts)} Reddit posts to migrate")
    
    # Show sample data
    print("\nSample posts:")
    for i, post in enumerate(posts[:3]):
        print(f"{i+1}. {post.get('title', 'No title')} ({post.get('subreddit', 'Unknown')})")
        print(f"   Link: {post.get('link', 'No link')}")
    
    # Migrate to PostgreSQL
    print("\nMigrating to PostgreSQL...")
    migrate_to_postgres(posts)
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    main() 