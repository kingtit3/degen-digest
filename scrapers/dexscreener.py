import json
from pathlib import Path

import requests

API_BASE = "https://api.dexscreener.com"


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
    # Example Solana token and pair for demonstration
    solana_token = "So11111111111111111111111111111111111111112"
    usdc_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    example_pair_id = "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN"  # Jupiter SOL/USDC
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
    Path("output/dexscreener_raw.json").write_text(json.dumps(data, indent=2))
    print("DEX Screener data saved to output/dexscreener_raw.json")


if __name__ == "__main__":
    main()
