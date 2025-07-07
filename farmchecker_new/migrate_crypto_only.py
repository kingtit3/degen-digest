#!/usr/bin/env python3
"""
Migrate crypto data from GCS to crypto_tokens table only
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
                
                file_migrated = 0
                
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
                        
                        file_migrated += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing token: {e}")
                        # Rollback the current transaction and continue
                        conn.rollback()
                        continue
                
                # Commit after each file to avoid long transactions
                conn.commit()
                total_migrated += file_migrated
                logger.info(f"✅ Migrated {blob.name} ({file_migrated} tokens)")
                
            except Exception as e:
                logger.error(f"Error processing file {blob.name}: {e}")
                conn.rollback()
                continue
        
        logger.info(f"🎉 Crypto migration complete! Migrated {total_migrated} tokens")
        return True
        
    except Exception as e:
        logger.error(f"❌ Crypto migration failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_crypto_data()
    if success:
        logger.info("✅ Crypto migration completed successfully!")
    else:
        logger.error("❌ Crypto migration failed!") 