import json
from pathlib import Path
import os
import psycopg2
import requests

API_BASE = "https://api.dexscreener.com"

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
        print(f"Database connection error: {e}")
        return None

def upsert_crypto_token(conn, token_data):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM crypto_tokens WHERE symbol = %s AND network = %s
        """, (token_data.get('symbol', ''), token_data.get('network', 'dexscreener')))
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
            print(f"Updated token: {token_data.get('symbol')} (ID: {token_id})")
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
                token_data.get('network', 'dexscreener'),
                token_data.get('contract_address', ''),
                token_data.get('market_cap', 0),
                token_data.get('price_usd', 0),
                token_data.get('volume_24h', 0),
                token_data.get('price_change_24h', 0)
            ))
            token_id = cursor.fetchone()[0]
            print(f"Inserted token: {token_data.get('symbol')} (ID: {token_id})")
        conn.commit()
        return token_id
    except Exception as e:
        print(f"Error upserting token {token_data.get('symbol')}: {e}")
        conn.rollback()
        return None

def fetch_latest_token_profiles():
    url = f"{API_BASE}/token-profiles/latest/v1"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def fetch_latest_boosted_tokens():
    url = f"{API_BASE}/token-boosts/latest/v1"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def fetch_top_boosted_tokens():
    url = f"{API_BASE}/token-boosts/top/v1"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def fetch_token_pairs(chain_id, token_address):
    url = f"{API_BASE}/token-pairs/v1/{chain_id}/{token_address}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def fetch_tokens_by_address(chain_id, token_addresses):
    url = f"{API_BASE}/tokens/v1/{chain_id}/{token_addresses}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def fetch_pair_by_id(chain_id, pair_id):
    url = f"{API_BASE}/latest/dex/pairs/{chain_id}/{pair_id}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def fetch_search_pairs(query):
    url = f"{API_BASE}/latest/dex/search"
    resp = requests.get(url, params={"q": query}, timeout=30)
    resp.raise_for_status()
    return resp.json()

def main():
    solana_token = "So11111111111111111111111111111111111111112"
    usdc_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    example_pair_id = "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN"
    chain_id = "solana"
    data = {
        "latest_token_profiles": fetch_latest_token_profiles(),
        "latest_boosted_tokens": fetch_latest_boosted_tokens(),
        "top_boosted_tokens": fetch_top_boosted_tokens(),
        "token_pairs": fetch_token_pairs(chain_id, solana_token),
        "tokens_by_address": fetch_tokens_by_address(
            chain_id, f"{solana_token},{usdc_token}"
        ),
        "pair_by_id": fetch_pair_by_id(chain_id, example_pair_id),
        "search_pairs": fetch_search_pairs("SOL/USDC"),
    }
    # Upsert tokens from latest_token_profiles
    conn = get_db_connection()
    if conn:
        profiles = data.get("latest_token_profiles", [])
        if isinstance(profiles, dict):
            profiles = profiles.get("tokens", [])
        for token in profiles:
            token_data = {
                'symbol': token.get('symbol', '').upper(),
                'name': token.get('name', ''),
                'network': token.get('chainId', 'dexscreener'),
                'contract_address': token.get('address', ''),
                'price_usd': token.get('priceUsd', 0),
                'price_change_24h': token.get('priceChange24h', 0),
                'market_cap': token.get('fdv', 0),
                'volume_24h': token.get('volume24h', 0)
            }
            upsert_crypto_token(conn, token_data)
        conn.close()
    Path("output/dexscreener_raw.json").write_text(json.dumps(data, indent=2))
    print("DEX Screener data saved to output/dexscreener_raw.json")

if __name__ == "__main__":
    main()
