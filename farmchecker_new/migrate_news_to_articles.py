#!/usr/bin/env python3
"""
Migration script to move news data from content_items to dedicated articles table
"""
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

# Add current directory to path
sys.path.append(".")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Use the same database configuration as server.py
        db_config = {
            "host": os.getenv("DB_HOST", "34.9.71.174"),
            "database": os.getenv("DB_NAME", "degen_digest"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "DegenDigest2024!"),
            "port": os.getenv("DB_PORT", "5432"),
        }
        
        conn = psycopg2.connect(
            **db_config,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def extract_article_metadata(raw_data: Optional[str]) -> Dict[str, Any]:
    """Extract metadata from raw_data JSON"""
    if not raw_data:
        return {}
    
    try:
        data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
        
        # Extract viral analysis data
        viral_potential = data.get("viral_potential", {})
        
        return {
            "viral_keywords": viral_potential.get("keywords", []),
            "sentiment": viral_potential.get("sentiment", "neutral"),
            "urgency": viral_potential.get("urgency", "low"),
            "category": viral_potential.get("category", "general"),
            "source_name": data.get("source", ""),
            "query": data.get("query", ""),
            "api_source": data.get("api_source", "newsapi.org"),
            "raw_data": data
        }
    except Exception as e:
        logger.warning(f"Error parsing raw_data: {e}")
        return {}

def migrate_news_data():
    """Migrate news data from content_items to articles table"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to connect to database")
            return False
        
        cursor = conn.cursor()
        
        # First, create the articles table
        logger.info("Creating articles table...")
        with open("create_articles_table.sql", "r") as f:
            create_sql = f.read()
            cursor.execute(create_sql)
        
        # Get all news articles from content_items
        logger.info("Fetching news articles from content_items...")
        cursor.execute("""
            SELECT ci.id, ci.title, ci.content, ci.author, ci.engagement_score,
                   ci.virality_score, ci.sentiment_score, ci.published_at, ci.url, ci.raw_data,
                   ci.created_at
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name = 'news'
            ORDER BY ci.created_at DESC
        """)
        
        news_articles = cursor.fetchall()
        logger.info(f"Found {len(news_articles)} news articles to migrate")
        
        # Migrate each article
        migrated_count = 0
        for article in news_articles:
            try:
                # Extract metadata from raw_data
                metadata = extract_article_metadata(article['raw_data'])
                
                # Insert into articles table
                cursor.execute("""
                    INSERT INTO articles (
                        title, description, content, url, source_name, author,
                        published_at, query, source_type, collected_at,
                        viral_keywords, sentiment, urgency, category,
                        engagement_score, virality_score, sentiment_score,
                        api_source, raw_data, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s
                    )
                """, (
                    article['title'],
                    None,  # description - not in content_items
                    article['content'],
                    article['url'],
                    metadata.get('source_name', ''),
                    article['author'],
                    article['published_at'],
                    metadata.get('query', ''),
                    'news',
                    article['created_at'],
                    json.dumps(metadata.get('viral_keywords', [])),
                    metadata.get('sentiment', 'neutral'),
                    metadata.get('urgency', 'low'),
                    metadata.get('category', 'general'),
                    article['engagement_score'] or 0,
                    article['virality_score'] or 0,
                    article['sentiment_score'] or 0,
                    metadata.get('api_source', 'newsapi.org'),
                    json.dumps(metadata.get('raw_data', {})),
                    article['created_at']
                ))
                
                migrated_count += 1
                
                if migrated_count % 100 == 0:
                    logger.info(f"Migrated {migrated_count} articles...")
                    
            except Exception as e:
                logger.error(f"Error migrating article {article['id']}: {e}")
                continue
        
        # Commit the transaction
        conn.commit()
        logger.info(f"Successfully migrated {migrated_count} news articles to articles table")
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) as count FROM articles")
        total_articles = cursor.fetchone()['count']
        logger.info(f"Total articles in new table: {total_articles}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def update_news_api_endpoint():
    """Update the news API to use the new articles table"""
    logger.info("Updating news API endpoint to use articles table...")
    
    # This would be done in the server.py file
    # For now, just log the change needed
    logger.info("""
    Update the /api/news-posts endpoint in server.py to use:
    
    SELECT id, title, content, author, engagement_score, virality_score, 
           sentiment_score, published_at, url, source_name, category, 
           sentiment, urgency, viral_keywords, raw_data
    FROM articles
    WHERE source_type = 'news'
    ORDER BY published_at DESC
    LIMIT 50
    """)

if __name__ == "__main__":
    logger.info("Starting news data migration...")
    
    if migrate_news_data():
        logger.info("Migration completed successfully!")
        update_news_api_endpoint()
    else:
        logger.error("Migration failed!")
        sys.exit(1) 