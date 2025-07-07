#!/usr/bin/env python3
"""
Migrate DexScreener data from GCS to dexscreener_pairs table only
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
        logger.error(f"❌ Failed to connect to database: {e}")
        return None

def get_gcs_client():
    """Create GCS client"""
    try:
        client = storage.Client()
        bucket = client.bucket('degen-digest-data')
        return client, bucket
    except Exception as e:
        logger.error(f"❌ Failed to create GCS client: {e}")
        return None, None

def migrate_dexscreener_data():
    """Migrate DexScreener data from GCS to dexscreener_pairs table"""
    logger.info("🔄 Starting DexScreener data migration...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    client, bucket = get_gcs_client()
    if not bucket:
        return False
    
    try:
        cursor = conn.cursor()
        
        # List all DexScreener files in GCS
        blobs = list(bucket.list_blobs(prefix="dexscreener_data/"))
        logger.info(f"Found {len(blobs)} DexScreener files to migrate")
        
        total_migrated = 0
        
        for blob in blobs:
            if not blob.name.endswith('.json'):
                continue
                
            try:
                # Download and parse JSON
                content = blob.download_as_text()
                data = json.loads(content)
                
                # Extract pairs from different possible keys
                pairs = []
                if 'token_pairs' in data and data['token_pairs']:
                    # token_pairs contains the actual pair data
                    pairs.extend(data['token_pairs'])
                # Skip pair_by_id as it contains string values, not pair objects
                # Skip search_pairs as it's a dict, not a list
                
                logger.info(f"Processing {blob.name} with {len(pairs)} pairs")
                
                if not pairs:
                    logger.info(f"✅ Migrated {blob.name} (0 pairs)")
                    continue
                
                file_migrated = 0
                
                for pair in pairs:
                    try:
                        # Extract pair data
                        pair_id = pair.get('pairAddress') or pair.get('pair_id') or pair.get('id')
                        if not pair_id:
                            continue
                            
                        base_token = pair.get('baseToken', {})
                        quote_token = pair.get('quoteToken', {})
                        dex = pair.get('dexId', 'unknown')
                        chain = pair.get('chainId', 'unknown')
                        
                        # Extract price data
                        price_usd = pair.get('priceUsd')
                        price_change_24h = pair.get('priceChange', {}).get('h24') if isinstance(pair.get('priceChange'), dict) else pair.get('priceChange24h')
                        
                        # Extract volume data
                        volume_24h = pair.get('volume', {}).get('h24') if isinstance(pair.get('volume'), dict) else pair.get('volume24h')
                        
                        # Extract liquidity data
                        liquidity_data = pair.get('liquidity', {})
                        liquidity_usd = liquidity_data.get('usd') if isinstance(liquidity_data, dict) else pair.get('liquidityUsd')
                        
                        # Extract transaction data
                        txns_data = pair.get('txns', {})
                        txns_24h = txns_data.get('h24', {}).get('buys', 0) + txns_data.get('h24', {}).get('sells', 0) if isinstance(txns_data, dict) else pair.get('txns24h')
                        
                        # Insert into database
                        cursor.execute("""
                            INSERT INTO dexscreener_pairs (
                                pair_id, chain_id, dex_id, pair_address,
                                base_token_symbol, base_token_name, base_token_address,
                                quote_token_symbol, quote_token_name, quote_token_address,
                                price_usd, price_change_24h, volume_24h, liquidity_usd, fdv,
                                txns_24h, buys_24h, sells_24h, collected_at, raw_data
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            ) ON CONFLICT (pair_id) DO NOTHING
                        """, (
                            pair_id,
                            chain,
                            dex,
                            pair_id,  # pair_address is the same as pair_id
                            base_token.get('symbol'),
                            base_token.get('name'),
                            base_token.get('address'),
                            quote_token.get('symbol'),
                            quote_token.get('name'),
                            quote_token.get('address'),
                            price_usd,
                            price_change_24h,
                            volume_24h,
                            liquidity_usd,
                            pair.get('fdv'),
                            txns_24h,
                            txns_data.get('h24', {}).get('buys', 0) if isinstance(txns_data, dict) else 0,
                            txns_data.get('h24', {}).get('sells', 0) if isinstance(txns_data, dict) else 0,
                            datetime.now(),
                            json.dumps(pair)
                        ))
                        
                        file_migrated += 1
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Error processing pair in {blob.name}: {e}")
                        continue
                
                conn.commit()
                total_migrated += file_migrated
                logger.info(f"✅ Migrated {blob.name} ({file_migrated} pairs)")
                
            except Exception as e:
                logger.error(f"❌ Error processing {blob.name}: {e}")
                conn.rollback()
                continue
        
        logger.info(f"🎉 DexScreener migration complete! Migrated {total_migrated} pairs")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_dexscreener_data()
    if success:
        logger.info("✅ DexScreener migration completed successfully!")
    else:
        logger.error("❌ DexScreener migration failed!") 