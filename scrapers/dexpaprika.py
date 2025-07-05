import json
from datetime import UTC, datetime
from pathlib import Path

import requests

API_BASE = "https://api.dexpaprika.com"


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
            "fetched_at": datetime.now(UTC).isoformat(),
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

    # Save to output
    out_path = Path("output/dexpaprika_raw.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2))
    print(f"DexPaprika data saved to {out_path}")
    print(f"Fetched data for {len(data['token_data'])} tokens")


if __name__ == "__main__":
    main()
