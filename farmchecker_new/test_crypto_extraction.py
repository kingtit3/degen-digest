#!/usr/bin/env python3
"""
Test crypto data extraction
"""

import json


def extract_crypto_data(raw_data):
    """Extract crypto market data from raw_data JSON"""
    try:
        if not raw_data:
            return {}

        data = raw_data if isinstance(raw_data, dict) else json.loads(raw_data)

        # Handle different crypto data structures based on migration script
        if "current_price" in data and "symbol" in data:
            # CoinGecko format (crypto source)
            return {
                "price": data.get("current_price", 0),
                "price_change_24h": data.get("price_change_24h", 0),
                "price_change_percentage_24h": data.get(
                    "price_change_percentage_24h", 0
                ),
                "market_cap": data.get("market_cap", 0),
                "volume_24h": data.get("total_volume", 0),
                "symbol": data.get("symbol", "").upper(),
                "name": data.get("name", ""),
                "image": data.get("image", ""),
                "rank": data.get("market_cap_rank", 0),
            }
        elif "priceUsd" in data:
            # DexScreener format
            return {
                "price": float(data.get("priceUsd", 0)),
                "price_change_24h": float(data.get("priceChange", {}).get("h24", 0)),
                "price_change_percentage_24h": float(
                    data.get("priceChange", {}).get("h24", 0)
                ),
                "market_cap": float(data.get("marketCap", 0)),
                "volume_24h": float(data.get("volume", {}).get("h24", 0)),
                "symbol": data.get("baseToken", {}).get("symbol", "").upper(),
                "name": data.get("baseToken", {}).get("name", ""),
                "image": data.get("baseToken", {}).get("image", ""),
                "rank": 0,
            }
        elif "price" in data and "symbol" in data:
            # DexPaprika format
            return {
                "price": float(data.get("price", 0)),
                "price_change_24h": float(data.get("price_change_24h", 0)),
                "price_change_percentage_24h": float(
                    data.get("price_change_percentage_24h", 0)
                ),
                "market_cap": float(data.get("market_cap", 0)),
                "volume_24h": float(data.get("volume_24h", 0)),
                "symbol": data.get("symbol", "").upper(),
                "name": data.get("name", ""),
                "image": data.get("image", ""),
                "rank": data.get("rank", 0),
            }
        elif "price_change" in data:
            # Generic format with price change
            return {
                "price": float(data.get("price", 0)),
                "price_change_24h": float(data.get("price_change", 0)),
                "price_change_percentage_24h": float(
                    data.get("price_change_percentage", 0)
                ),
                "market_cap": float(data.get("market_cap", 0)),
                "volume_24h": float(data.get("volume", 0)),
                "symbol": data.get("symbol", "").upper(),
                "name": data.get("name", ""),
                "image": data.get("image", ""),
                "rank": data.get("rank", 0),
            }
        else:
            # Try to extract basic info from any structure
            return {
                "price": float(data.get("price", 0)),
                "price_change_24h": 0,
                "price_change_percentage_24h": 0,
                "market_cap": float(data.get("market_cap", 0)),
                "volume_24h": float(data.get("volume", 0)),
                "symbol": str(data.get("symbol", data.get("name", ""))).upper(),
                "name": str(data.get("name", data.get("symbol", ""))),
                "image": data.get("image", ""),
                "rank": data.get("rank", 0),
            }

    except Exception as e:
        print(f"Error extracting crypto data: {e}")
        return {}


def test_extraction():
    """Test the extraction function with sample data"""

    # Test CoinGecko format
    coingecko_data = {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 45000.0,
        "market_cap": 850000000000,
        "market_cap_rank": 1,
        "total_volume": 25000000000,
        "price_change_24h": 1250.0,
        "price_change_percentage_24h": 2.85,
        "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
    }

    # Test DexScreener format
    dexscreener_data = {
        "priceUsd": "120.50",
        "priceChange": {"h24": 8.50},
        "marketCap": 52000000000,
        "volume": {"h24": 2800000000},
        "baseToken": {
            "symbol": "SOL",
            "name": "Solana",
            "image": "https://assets.coingecko.com/coins/images/4128/large/solana.png",
        },
    }

    # Test DexPaprika format
    dexpaprika_data = {
        "price": 0.85,
        "price_change_24h": 0.02,
        "price_change_percentage_24h": 2.41,
        "market_cap": 30000000000,
        "volume_24h": 1200000000,
        "symbol": "ADA",
        "name": "Cardano",
        "image": "https://assets.coingecko.com/coins/images/975/large/cardano.png",
        "rank": 8,
    }

    print("Testing CoinGecko format:")
    result1 = extract_crypto_data(coingecko_data)
    print(json.dumps(result1, indent=2))

    print("\nTesting DexScreener format:")
    result2 = extract_crypto_data(dexscreener_data)
    print(json.dumps(result2, indent=2))

    print("\nTesting DexPaprika format:")
    result3 = extract_crypto_data(dexpaprika_data)
    print(json.dumps(result3, indent=2))

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    test_extraction()
