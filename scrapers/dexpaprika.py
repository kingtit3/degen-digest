import json
from datetime import datetime, timezone
from pathlib import Path
import os
import psycopg2
import requests

API_BASE = "https://api.dexpaprika.com"

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
        """, (token_data.get('symbol', ''), token_data.get('network', 'dexpaprika')))
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
                token_data.get('network', 'dexpaprika'),
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

def fetch_token_data(network_id: str, token_address: str):
    """Fetch detailed token data from DexPaprika"""
    url = f"{API_BASE}/networks/{network_id}/tokens/{token_address}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_networks():
    """Fetch supported networks"""
    url = f"{API_BASE}/networks"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_token_prices(network_id: str, token_addresses: list):
    """Fetch prices for multiple tokens"""
    results = []
    for address in token_addresses:
        try:
            data = fetch_token_data(network_id, address)
            results.append(data)
        except Exception as e:
            print(f"Error fetching {address}: {e}")
    return results


def main():
    # Example Solana tokens to track
    solana_tokens = [
        "So11111111111111111111111111111111111111112",  # SOL
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
        "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",  # POPCAT
    ]

    network_id = "solana"

    data = {
        "metadata": {
            "source": "dexpaprika",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "network": network_id,
            "tokens_tracked": len(solana_tokens),
        },
        "networks": fetch_networks(),
        "token_data": fetch_token_prices(network_id, solana_tokens),
        "summary": {
            "total_tokens": len(solana_tokens),
            "network_id": network_id,
            "api_version": "v1",
        },
    }

    # Upsert each token into crypto_tokens
    conn = get_db_connection()
    if conn:
        for token in data["token_data"]:
            token_data = {
                'symbol': token.get('symbol', '').upper(),
                'name': token.get('name', ''),
                'network': network_id,
                'contract_address': token.get('address', ''),
                'price_usd': token.get('price_usd', 0),
                'price_change_24h': token.get('price_change_24h', 0),
                'market_cap': token.get('fdv', 0),
                'volume_24h': token.get('volume_usd', 0)
            }
            upsert_crypto_token(conn, token_data)
        conn.close()

    # Save to output
    out_path = Path("output/dexpaprika_raw.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2))
    print(f"DexPaprika data saved to {out_path}")
    print(f"Fetched data for {len(data['token_data'])} tokens")


if __name__ == "__main__":
    main()
