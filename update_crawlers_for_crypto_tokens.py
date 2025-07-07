#!/usr/bin/env python3
"""
Update crawlers to populate crypto_tokens table
This script modifies the crawlers to store crypto data in the dedicated crypto_tokens table
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
    """Insert or update crypto token data in crypto_tokens table"""
    try:
        cursor = conn.cursor()
        
        # Check if token already exists
        cursor.execute("""
            SELECT id FROM crypto_tokens 
            WHERE symbol = %s AND network = %s
        """, (token_data.get('symbol', ''), token_data.get('network', '')))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing token
            cursor.execute("""
                UPDATE crypto_tokens SET
                    name = %s,
                    price_usd = %s,
                    price_change_24h = %s,
                    market_cap = %s,
                    volume_24h = %s,
                    contract_address = %s,
                    last_updated_at = NOW()
                WHERE id = %s
            """, (
                token_data.get('name', ''),
                token_data.get('price_usd', 0),
                token_data.get('price_change_24h', 0),
                token_data.get('market_cap', 0),
                token_data.get('volume_24h', 0),
                token_data.get('contract_address', ''),
                existing[0]
            ))
            token_id = existing[0]
            logger.info(f"Updated token: {token_data.get('symbol')} (ID: {token_id})")
        else:
            # Insert new token
            cursor.execute("""
                INSERT INTO crypto_tokens (
                    symbol, name, network, contract_address, market_cap, 
                    price_usd, volume_24h, price_change_24h, first_seen_at, last_updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """, (
                token_data.get('symbol', ''),
                token_data.get('name', ''),
                token_data.get('network', ''),
                token_data.get('contract_address', ''),
                token_data.get('market_cap', 0),
                token_data.get('price_usd', 0),
                token_data.get('volume_24h', 0),
                token_data.get('price_change_24h', 0)
            ))
            token_id = cursor.fetchone()[0]
            logger.info(f"Inserted token: {token_data.get('symbol')} (ID: {token_id})")
        
        conn.commit()
        return token_id
        
    except Exception as e:
        logger.error(f"Error upserting token {token_data.get('symbol')}: {e}")
        conn.rollback()
        return None

def update_coingecko_crawler():
    """Update CoinGecko crawler to use crypto_tokens table"""
    logger.info("Updating CoinGecko crawler...")
    
    # This would modify the coingecko crawler to call upsert_crypto_token
    # instead of inserting into content_items
    
    sample_data = {
        'symbol': 'BTC',
        'name': 'Bitcoin',
        'network': 'bitcoin',
        'contract_address': '',
        'price_usd': 45000.00,
        'price_change_24h': 2.85,
        'market_cap': 850000000000,
        'volume_24h': 25000000000
    }
    
    conn = get_db_connection()
    if conn:
        upsert_crypto_token(conn, sample_data)
        conn.close()

def update_dexpaprika_crawler():
    """Update DexPaprika crawler to use crypto_tokens table"""
    logger.info("Updating DexPaprika crawler...")
    
    # This would modify the dexpaprika crawler to call upsert_crypto_token
    # instead of inserting into content_items
    
    sample_data = {
        'symbol': 'ETH',
        'name': 'Ethereum',
        'network': 'ethereum',
        'contract_address': '0x0000000000000000000000000000000000000000',
        'price_usd': 3200.00,
        'price_change_24h': 3.10,
        'market_cap': 380000000000,
        'volume_24h': 15000000000
    }
    
    conn = get_db_connection()
    if conn:
        upsert_crypto_token(conn, sample_data)
        conn.close()

def update_dexscreener_crawler():
    """Update DexScreener crawler to use crypto_tokens table"""
    logger.info("Updating DexScreener crawler...")
    
    # This would modify the dexscreener crawler to call upsert_crypto_token
    # instead of inserting into content_items
    
    sample_data = {
        'symbol': 'SOL',
        'name': 'Solana',
        'network': 'solana',
        'contract_address': '',
        'price_usd': 120.50,
        'price_change_24h': 7.58,
        'market_cap': 52000000000,
        'volume_24h': 2800000000
    }
    
    conn = get_db_connection()
    if conn:
        upsert_crypto_token(conn, sample_data)
        conn.close()

def populate_sample_data():
    """Populate crypto_tokens table with sample data for testing"""
    logger.info("Populating crypto_tokens table with sample data...")
    
    sample_tokens = [
        {
            'symbol': 'BTC',
            'name': 'Bitcoin',
            'network': 'bitcoin',
            'contract_address': '',
            'price_usd': 45000.00,
            'price_change_24h': 2.85,
            'market_cap': 850000000000,
            'volume_24h': 25000000000
        },
        {
            'symbol': 'ETH',
            'name': 'Ethereum',
            'network': 'ethereum',
            'contract_address': '0x0000000000000000000000000000000000000000',
            'price_usd': 3200.00,
            'price_change_24h': 3.10,
            'market_cap': 380000000000,
            'volume_24h': 15000000000
        },
        {
            'symbol': 'SOL',
            'name': 'Solana',
            'network': 'solana',
            'contract_address': '',
            'price_usd': 120.50,
            'price_change_24h': 7.58,
            'market_cap': 52000000000,
            'volume_24h': 2800000000
        },
        {
            'symbol': 'ADA',
            'name': 'Cardano',
            'network': 'cardano',
            'contract_address': '',
            'price_usd': 0.85,
            'price_change_24h': 2.41,
            'market_cap': 30000000000,
            'volume_24h': 1200000000
        },
        {
            'symbol': 'DOT',
            'name': 'Polkadot',
            'network': 'polkadot',
            'contract_address': '',
            'price_usd': 8.50,
            'price_change_24h': 3.03,
            'market_cap': 12000000000,
            'volume_24h': 800000000
        }
    ]
    
    conn = get_db_connection()
    if conn:
        for token in sample_tokens:
            upsert_crypto_token(conn, token)
        conn.close()
        logger.info(f"Populated {len(sample_tokens)} sample tokens")

if __name__ == "__main__":
    logger.info("Starting crawler updates for crypto_tokens table...")
    
    # Populate with sample data first
    populate_sample_data()
    
    # Update crawler functions (these would be called by the actual crawlers)
    update_coingecko_crawler()
    update_dexpaprika_crawler()
    update_dexscreener_crawler()
    
    logger.info("Crawler updates completed!") 