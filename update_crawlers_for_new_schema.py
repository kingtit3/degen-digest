#!/usr/bin/env python3
"""
Update crawlers to use new crypto_tokens table schema
This script modifies the crawlers to store data in the dedicated crypto_tokens table
"""

import json
import logging
import os
import psycopg2
from datetime import datetime

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

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def upsert_crypto_token(conn, token_data):
    """Insert or update crypto token data using the new schema"""
    try:
        cursor = conn.cursor()
        
        # Call the upsert function
        cursor.execute("""
            SELECT upsert_crypto_token(
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            token_data.get('symbol', ''),
            token_data.get('name', ''),
            token_data.get('price_usd', 0),
            token_data.get('price_change_24h', 0),
            token_data.get('price_change_percentage_24h', 0),
            token_data.get('market_cap_usd', 0),
            token_data.get('volume_24h_usd', 0),
            token_data.get('rank', 0),
            token_data.get('image_url', ''),
            token_data.get('source', ''),
            token_data.get('external_id', ''),
            json.dumps(token_data.get('raw_data', {}))
        ))
        
        token_id = cursor.fetchone()[0]
        conn.commit()
        logger.info(f"Upserted token: {token_data.get('symbol')} (ID: {token_id})")
        return token_id
        
    except Exception as e:
        logger.error(f"Error upserting token {token_data.get('symbol')}: {e}")
        conn.rollback()
        return None

def migrate_existing_data():
    """Migrate existing crypto data from content_items to crypto_tokens"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get existing crypto data from content_items
        cursor.execute("""
            SELECT id, source_id, title, content, raw_data 
            FROM content_items 
            WHERE raw_data IS NOT NULL 
            AND (title LIKE '%STETH%' OR title LIKE '%LIDO%' OR content LIKE '%price%')
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        logger.info(f"Found {len(rows)} existing crypto records to migrate")
        
        migrated_count = 0
        for row in rows:
            try:
                # Parse the existing data
                raw_data = row[4] if isinstance(row[4], dict) else json.loads(row[4])
                
                # Extract token information based on source
                token_data = {
                    'symbol': '',
                    'name': '',
                    'price_usd': 0,
                    'price_change_24h': 0,
                    'price_change_percentage_24h': 0,
                    'market_cap_usd': 0,
                    'volume_24h_usd': 0,
                    'rank': 0,
                    'image_url': '',
                    'source': 'unknown',
                    'external_id': str(row[0]),
                    'raw_data': raw_data
                }
                
                # Try to extract symbol from title
                if row[2]:  # title
                    title = row[2]
                    if 'STETH' in title:
                        token_data['symbol'] = 'STETH'
                        token_data['name'] = 'Lido Staked Ether'
                        token_data['source'] = 'coingecko'
                    elif 'LIDO' in title:
                        token_data['symbol'] = 'LIDO'
                        token_data['name'] = 'Lido DAO'
                        token_data['source'] = 'coingecko'
                
                # Try to extract price from content
                if row[3]:  # content
                    content = row[3]
                    if '$' in content:
                        try:
                            price_str = content.split('$')[1].split()[0]
                            token_data['price_usd'] = float(price_str.replace(',', ''))
                        except:
                            pass
                
                # Try to extract price change from raw_data
                if 'price_change' in raw_data:
                    token_data['price_change_percentage_24h'] = float(raw_data['price_change'])
                
                if token_data['symbol']:
                    upsert_crypto_token(conn, token_data)
                    migrated_count += 1
                    
            except Exception as e:
                logger.error(f"Error migrating row {row[0]}: {e}")
                continue
        
        logger.info(f"Successfully migrated {migrated_count} tokens")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
    finally:
        conn.close()

def update_web_app_queries():
    """Update the web app to query the new crypto_tokens table"""
    logger.info("Updating web app queries to use new crypto_tokens table...")
    
    # The web app should now query the latest_crypto_tokens view instead of content_items
    # This will be implemented in the server.py file

if __name__ == "__main__":
    logger.info("Starting database schema migration...")
    
    # First, run the SQL schema upgrade
    logger.info("Please run the database_schema_upgrade.sql script first")
    
    # Then migrate existing data
    migrate_existing_data()
    
    # Update web app queries
    update_web_app_queries()
    
    logger.info("Migration completed!") 