#!/usr/bin/env python3
"""
Migrate DEX data from GCS to dex_pairs table only
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
                
                file_migrated = 0
                
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
                            pair.get('base_token_symbol'),
                            pair.get('base_token_name'),
                            pair.get('base_token_address'),
                            pair.get('quote_token_symbol'),
                            pair.get('quote_token_name'),
                            pair.get('quote_token_address'),
                            pair.get('dex_name'),
                            pair.get('chain_name'),
                            pair.get('price_usd'),
                            pair.get('price_change_24h'),
                            pair.get('volume_24h'),
                            pair.get('liquidity_usd'),
                            pair.get('market_cap'),
                            pair.get('txns_24h'),
                            pair.get('fdv'),
                            'dexscreener',
                            pair.get('published_at') or datetime.now(),
                            datetime.now(),
                            json.dumps(pair)
                        ))
                        
                        file_migrated += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing pair: {e}")
                        # Rollback the current transaction and continue
                        conn.rollback()
                        continue
                
                # Commit after each file to avoid long transactions
                conn.commit()
                total_migrated += file_migrated
                logger.info(f"✅ Migrated {blob.name} ({file_migrated} pairs)")
                
            except Exception as e:
                logger.error(f"Error processing file {blob.name}: {e}")
                conn.rollback()
                continue
        
        # Migrate DexPaprika data
        dexpaprika_blobs = list(bucket.list_blobs(prefix="dexpaprika_data/"))
        logger.info(f"Found {len(dexpaprika_blobs)} DexPaprika files to migrate")
        
        # Process DexPaprika files
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
                
                file_migrated = 0
                
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
                            pair.get('base_token_symbol'),
                            pair.get('base_token_name'),
                            pair.get('base_token_address'),
                            pair.get('quote_token_symbol'),
                            pair.get('quote_token_name'),
                            pair.get('quote_token_address'),
                            pair.get('dex_name'),
                            pair.get('chain_name'),
                            pair.get('price_usd'),
                            pair.get('price_change_24h'),
                            pair.get('volume_24h'),
                            pair.get('liquidity_usd'),
                            pair.get('market_cap'),
                            pair.get('txns_24h'),
                            pair.get('fdv'),
                            'dexpaprika',
                            pair.get('published_at') or datetime.now(),
                            datetime.now(),
                            json.dumps(pair)
                        ))
                        
                        file_migrated += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing pair: {e}")
                        # Rollback the current transaction and continue
                        conn.rollback()
                        continue
                
                # Commit after each file to avoid long transactions
                conn.commit()
                total_migrated += file_migrated
                logger.info(f"✅ Migrated {blob.name} ({file_migrated} pairs)")
                
            except Exception as e:
                logger.error(f"Error processing file {blob.name}: {e}")
                conn.rollback()
                continue
        
        logger.info(f"🎉 DEX migration complete! Migrated {total_migrated} pairs")
        return True
        
    except Exception as e:
        logger.error(f"❌ DEX migration failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_dex_data()
    if success:
        logger.info("✅ DEX migration completed successfully!")
    else:
        logger.error("❌ DEX migration failed!") 