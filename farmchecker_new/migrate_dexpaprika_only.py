#!/usr/bin/env python3
"""
Migrate DexPaprika data from GCS to dexpaprika_pairs table only
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

def migrate_dexpaprika_data():
    """Migrate DexPaprika data from GCS to dexpaprika_pairs table"""
    logger.info("🔄 Starting DexPaprika data migration...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    client, bucket = get_gcs_client()
    if not bucket:
        return False
    
    try:
        cursor = conn.cursor()
        
        # List all DexPaprika files in GCS
        blobs = list(bucket.list_blobs(prefix="dexpaprika_data/"))
        logger.info(f"Found {len(blobs)} DexPaprika files to migrate")
        
        total_migrated = 0
        
        for blob in blobs:
            if not blob.name.endswith('.json'):
                continue
                
            try:
                # Download and parse JSON
                content = blob.download_as_text()
                data = json.loads(content)
                
                # Extract pairs from token_data
                pairs = []
                if 'token_data' in data and data['token_data']:
                    # token_data contains token information with summary
                    pairs = data['token_data']
                
                logger.info(f"Processing {blob.name} with {len(pairs)} tokens")
                
                if not pairs:
                    logger.info(f"✅ Migrated {blob.name} (0 tokens)")
                    continue
                
                file_migrated = 0
                
                for token in pairs:
                    try:
                        # Extract token data - DexPaprika structure is different
                        token_id = token.get('id') or token.get('address')
                        if not token_id:
                            continue
                            
                        # Extract token information
                        base_token_symbol = token.get('symbol')
                        base_token_name = token.get('name')
                        base_token_address = token.get('id') or token.get('address')
                        
                        # For DexPaprika, we're storing token data, not pairs
                        # Use the token address as pair_id for consistency
                        pair_id = f"dexpaprika_{token_id}"
                        
                        dex_name = 'dexpaprika'
                        chain_name = token.get('chain', 'unknown')
                        
                        # Extract summary data
                        summary = token.get('summary', {})
                        price_usd = summary.get('price_usd')
                        volume_24h = summary.get('24h', {}).get('volume_usd') if isinstance(summary.get('24h'), dict) else None
                        liquidity_usd = summary.get('liquidity_usd')
                        txns_24h = summary.get('24h', {}).get('txns') if isinstance(summary.get('24h'), dict) else None
                        fdv = summary.get('fdv')
                        
                        # Calculate price change from summary
                        price_change_24h = summary.get('24h', {}).get('last_price_usd_change') if isinstance(summary.get('24h'), dict) else None
                        
                        # Insert into database
                        cursor.execute("""
                            INSERT INTO dexpaprika_pairs (
                                pair_id, chain_id, dex_id, pair_address,
                                base_token_symbol, base_token_name, base_token_address,
                                quote_token_symbol, quote_token_name, quote_token_address,
                                price_usd, price_change_24h, volume_24h, liquidity_usd,
                                txns_24h, market_cap, collected_at, raw_data
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            ) ON CONFLICT (pair_id) DO NOTHING
                        """, (
                            pair_id,
                            chain_name,
                            dex_name,
                            base_token_address,  # Use token address as pair_address
                            base_token_symbol,
                            base_token_name,
                            base_token_address,
                            'N/A',  # No quote token for DexPaprika
                            'N/A',  # No quote token for DexPaprika
                            'N/A',  # No quote token for DexPaprika
                            price_usd,
                            price_change_24h,
                            volume_24h,
                            liquidity_usd,
                            txns_24h,
                            None,  # No market cap in DexPaprika
                            datetime.now(),
                            json.dumps(token)
                        ))
                        
                        file_migrated += 1
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Error processing token in {blob.name}: {e}")
                        continue
                
                conn.commit()
                total_migrated += file_migrated
                logger.info(f"✅ Migrated {blob.name} ({file_migrated} tokens)")
                
            except Exception as e:
                logger.error(f"❌ Error processing {blob.name}: {e}")
                conn.rollback()
                continue
        
        logger.info(f"🎉 DexPaprika migration complete! Migrated {total_migrated} tokens")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_dexpaprika_data()
    if success:
        logger.info("✅ DexPaprika migration completed successfully!")
    else:
        logger.error("❌ DexPaprika migration failed!") 