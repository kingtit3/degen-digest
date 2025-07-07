import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import UTC, datetime, timezone
from pathlib import Path

import httpx
import psycopg2

from utils.advanced_logging import get_logger
from utils.logger import setup_logging

setup_logging()
logger = get_logger(__name__)

API_URL = "https://api.coingecko.com/api/v3/coins/markets"

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "34.9.71.174"),
    "database": os.getenv("DB_NAME", "degen_digest"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "DegenDigest2024!"),
    "port": os.getenv("DB_PORT", "5432"),
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def upsert_crypto_token(conn, token_data):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM crypto_tokens WHERE symbol = %s AND network = %s
        """, (token_data.get('symbol', ''), token_data.get('network', 'coingecko')))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE crypto_tokens SET
                    name = %s,
                    price_usd = %s,
                    price_change_24h = %s,
                    market_cap = %s,
                    volume_24h = %s,
                    last_updated_at = NOW()
                WHERE id = %s
            """, (
                token_data.get('name', ''),
                token_data.get('price_usd', 0),
                token_data.get('price_change_24h', 0),
                token_data.get('market_cap', 0),
                token_data.get('volume_24h', 0),
                existing[0]
            ))
            token_id = existing[0]
            logger.info(f"Updated token: {token_data.get('symbol')} (ID: {token_id})")
        else:
            cursor.execute("""
                INSERT INTO crypto_tokens (
                    symbol, name, network, contract_address, market_cap, 
                    price_usd, volume_24h, price_change_24h, first_seen_at, last_updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """, (
                token_data.get('symbol', ''),
                token_data.get('name', ''),
                token_data.get('network', 'coingecko'),
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

def fetch_top_gainers(limit: int = 20) -> list[dict]:
    params = {
        "vs_currency": "usd",
        "order": "price_change_percentage_24h_desc",
        "per_page": limit,
        "page": 1,
        "price_change_percentage": "24h",
    }
    logger.info("coingecko request", limit=limit)
    resp = httpx.get(API_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data

def main():
    items = fetch_top_gainers(20)
    conn = get_db_connection()
    if not conn:
        logger.error("Could not connect to DB")
        return
    for coin in items:
        token_data = {
            'symbol': coin.get('symbol', '').upper(),
            'name': coin.get('name', ''),
            'network': 'coingecko',
            'contract_address': '',
            'price_usd': coin.get('current_price', 0),
            'price_change_24h': coin.get('price_change_percentage_24h', 0),
            'market_cap': coin.get('market_cap', 0),
            'volume_24h': coin.get('total_volume', 0)
        }
        upsert_crypto_token(conn, token_data)
    conn.close()
    out_path = Path("output/coingecko_raw.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(items, indent=2))
    logger.info("coingecko gainers saved", count=len(items))

if __name__ == "__main__":
    main()
