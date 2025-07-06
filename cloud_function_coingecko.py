#!/usr/bin/env python3
"""
Enhanced CoinGecko Cloud Function - Standalone Version
"""
import json
import logging
import os
from datetime import UTC, datetime
from typing import Any, Dict

import functions_framework
import requests
from google.cloud import storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_viral_keywords(text: str) -> list[str]:
    """Extract viral keywords from text"""
    viral_keywords = [
        # Memecoin keywords
        "moon",
        "pump",
        "100x",
        "1000x",
        "gem",
        "next gem",
        "pepe",
        "doge",
        "shib",
        "floki",
        "wojak",
        "chad",
        "based",
        "degen",
        "mooning",
        "pumping",
        "fomo",
        "fud",
        "hodl",
        "diamond hands",
        "wen",
        "ser",
        "ngmi",
        "wagmi",
        "gm",
        "gn",
        "gm fam",
        "gm ser",
        "gm king",
        "gm queen",
        # Launchpad keywords
        "launchpad",
        "ido",
        "initial dex offering",
        "token launch",
        "presale",
        "fair launch",
        "stealth launch",
        "pinksale",
        "dxsale",
        "bounce",
        "polkastarter",
        "daomaker",
        "trustpad",
        "seedify",
        "gamefi",
        "new token",
        "ico",
        "initial coin offering",
        "whitelist",
        "kyc",
        # Airdrop keywords
        "airdrop",
        "free tokens",
        "claim",
        "eligibility",
        "snapshot",
        "whitelist",
        "retroactive",
        "community airdrop",
        "token distribution",
        "free crypto",
        "claim now",
        "don't miss out",
        # Farming keywords
        "yield farming",
        "farming",
        "liquidity mining",
        "staking",
        "apy",
        "apr",
        "rewards",
        "harvest",
        "compound",
        "auto compound",
        "vault",
        "strategy",
        "defi farming",
        "liquidity provider",
        "lp",
        "amm",
        "dex farming",
        "impermanent loss",
        "yield optimizer",
        # Solana keywords
        "solana",
        "sol",
        "phantom",
        "solflare",
        "raydium",
        "orca",
        "serum",
        "jupiter",
        "pyth",
        "bonk",
        "dogwifhat",
        "samoyedcoin",
        "marinade",
        "jito",
        "tensor",
        "magic eden",
        "saga",
        "firedancer",
        "solana mobile",
        "solana pay",
        "spl",
        "spl token",
        # Urgency keywords
        "now",
        "today",
        "live",
        "breaking",
        "urgent",
        "don't miss",
        "last chance",
        "limited time",
        "expires",
        "deadline",
        "hurry",
        "quick",
        "fast",
        "immediate",
        "instant",
        "right now",
        # Viral keywords
        "viral",
        "trending",
        "hot",
        "fire",
        "lit",
        "savage",
        "epic",
        "legendary",
        "insane",
        "crazy",
        "wild",
        "amazing",
        "incredible",
        "unbelievable",
        "mind blowing",
        "game changer",
    ]

    text_lower = text.lower()
    found_keywords = []

    for keyword in viral_keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)

    return found_keywords


def analyze_sentiment(text: str) -> str:
    """Simple sentiment analysis"""
    positive_words = [
        "moon",
        "pump",
        "bull",
        "bullish",
        "mooning",
        "pumping",
        "gem",
        "based",
        "chad",
        "wagmi",
        "gm",
        "fire",
        "lit",
        "savage",
        "epic",
        "legendary",
        "insane",
        "crazy",
        "wild",
        "amazing",
        "incredible",
        "unbelievable",
        "mind blowing",
        "game changer",
    ]
    negative_words = [
        "dump",
        "bear",
        "bearish",
        "fud",
        "ngmi",
        "scam",
        "rug",
        "dead",
        "failed",
        "lose",
        "loss",
        "crash",
        "dump",
        "sell",
        "panic",
    ]

    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def detect_urgency(text: str) -> str:
    """Detect urgency level in text"""
    urgent_words = [
        "now",
        "today",
        "live",
        "breaking",
        "urgent",
        "don't miss",
        "last chance",
        "limited time",
        "expires",
        "deadline",
        "hurry",
        "quick",
        "fast",
        "immediate",
        "instant",
        "right now",
    ]

    text_lower = text.lower()
    urgent_count = sum(1 for word in urgent_words if word in text_lower)

    if urgent_count >= 3:
        return "high"
    elif urgent_count >= 1:
        return "medium"
    else:
        return "low"


def crawl_coingecko() -> dict[str, Any]:
    """Enhanced CoinGecko crawl focused on viral content sources"""
    try:
        logger.info("🔄 Starting Enhanced CoinGecko crawl for viral content...")

        # Enhanced CoinGecko API endpoints focused on viral content
        endpoints = [
            # Trending coins (most viral)
            {
                "name": "trending",
                "url": "https://api.coingecko.com/api/v3/search/trending",
                "category": "trending",
            },
            # Top gainers (pumping)
            {
                "name": "top_gainers",
                "url": "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=price_change_percentage_24h_desc&per_page=100&page=1&sparkline=false",
                "category": "gainers",
            },
            # Top losers (dumping)
            {
                "name": "top_losers",
                "url": "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=price_change_percentage_24h_asc&per_page=100&page=1&sparkline=false",
                "category": "losers",
            },
            # New coins (launches)
            {
                "name": "new_coins",
                "url": "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=created_desc&per_page=100&page=1&sparkline=false",
                "category": "launches",
            },
            # Solana ecosystem
            {
                "name": "solana_coins",
                "url": "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=solana,bonk,dogwifhat,samoyedcoin,marinade,jito&order=market_cap_desc&per_page=50&page=1&sparkline=false",
                "category": "solana",
            },
            # Memecoins
            {
                "name": "memecoins",
                "url": "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=dogecoin,shiba-inu,pepe,floki,wojak&order=market_cap_desc&per_page=50&page=1&sparkline=false",
                "category": "memecoin",
            },
            # DeFi tokens
            {
                "name": "defi_tokens",
                "url": "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=decentralized-finance-defi&order=market_cap_desc&per_page=100&page=1&sparkline=false",
                "category": "defi",
            },
            # Gaming tokens
            {
                "name": "gaming_tokens",
                "url": "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=gaming&order=market_cap_desc&per_page=100&page=1&sparkline=false",
                "category": "gaming",
            },
        ]

        all_coins = []
        endpoint_stats = {}

        for endpoint in endpoints:
            try:
                logger.info(
                    f"  📥 Fetching {endpoint['name']} ({endpoint['category']})..."
                )

                response = requests.get(endpoint["url"], timeout=15)

                if response.status_code == 200:
                    data = response.json()

                    # Handle different response formats
                    if endpoint["name"] == "trending":
                        coins = data.get("coins", [])
                        processed_coins = []
                        for coin_data in coins:
                            coin = coin_data.get("item", {})
                            if coin:
                                processed_coin = {
                                    "id": coin.get("id", ""),
                                    "symbol": coin.get("symbol", "").upper(),
                                    "name": coin.get("name", ""),
                                    "market_cap_rank": coin.get("market_cap_rank", 0),
                                    "price_btc": coin.get("price_btc", 0),
                                    "score": coin.get("score", 0),
                                    "category": endpoint["category"],
                                    "source": "coingecko",
                                    "published": datetime.now(UTC).isoformat(),
                                    "viral_potential": {
                                        "keywords": extract_viral_keywords(
                                            coin.get("name", "")
                                        ),
                                        "sentiment": analyze_sentiment(
                                            coin.get("name", "")
                                        ),
                                        "urgency": detect_urgency(coin.get("name", "")),
                                    },
                                }
                                processed_coins.append(processed_coin)
                    else:
                        # Standard market data format
                        processed_coins = []
                        for coin in data:
                            if coin.get("id") and coin.get("symbol"):
                                processed_coin = {
                                    "id": coin.get("id", ""),
                                    "symbol": coin.get("symbol", "").upper(),
                                    "name": coin.get("name", ""),
                                    "current_price": coin.get("current_price", 0),
                                    "market_cap": coin.get("market_cap", 0),
                                    "market_cap_rank": coin.get("market_cap_rank", 0),
                                    "total_volume": coin.get("total_volume", 0),
                                    "price_change_percentage_24h": coin.get(
                                        "price_change_percentage_24h", 0
                                    ),
                                    "price_change_percentage_7d": coin.get(
                                        "price_change_percentage_7d", 0
                                    ),
                                    "circulating_supply": coin.get(
                                        "circulating_supply", 0
                                    ),
                                    "total_supply": coin.get("total_supply", 0),
                                    "max_supply": coin.get("max_supply", 0),
                                    "ath": coin.get("ath", 0),
                                    "ath_change_percentage": coin.get(
                                        "ath_change_percentage", 0
                                    ),
                                    "category": endpoint["category"],
                                    "source": "coingecko",
                                    "published": datetime.now(UTC).isoformat(),
                                    "viral_potential": {
                                        "keywords": extract_viral_keywords(
                                            coin.get("name", "")
                                        ),
                                        "sentiment": analyze_sentiment(
                                            coin.get("name", "")
                                        ),
                                        "urgency": detect_urgency(coin.get("name", "")),
                                    },
                                }
                                processed_coins.append(processed_coin)

                    # Limit to top 20 coins per endpoint for viral content
                    all_coins.extend(processed_coins[:20])

                    # Update endpoint stats
                    endpoint_stats[endpoint["name"]] = len(processed_coins[:20])

                    logger.info(
                        f"  ✅ {endpoint['name']}: {len(processed_coins)} coins"
                    )
                else:
                    logger.warning(
                        f"  ⚠️ Failed to fetch {endpoint['name']}: HTTP {response.status_code}"
                    )

            except Exception as e:
                logger.error(f"  ❌ Error fetching {endpoint['name']}: {e}")

        data = {
            "coins": all_coins,
            "metadata": {
                "source": "coingecko",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "success",
                "total_coins": len(all_coins),
                "endpoints": list(endpoint_stats.keys()),
                "endpoint_stats": endpoint_stats,
                "endpoints_processed": len(endpoints),
                "viral_content_focus": True,
            },
        }

        logger.info(
            f"✅ Enhanced CoinGecko crawl completed: {len(all_coins)} coins from {len(endpoints)} endpoints"
        )
        logger.info(f"📊 Endpoint breakdown: {endpoint_stats}")
        return data

    except Exception as e:
        logger.error(f"❌ Enhanced CoinGecko crawl failed: {e}")
        return {
            "coins": [],
            "metadata": {
                "source": "coingecko",
                "crawled_at": datetime.now().isoformat(),
                "status": "error",
                "error": str(e),
                "total_coins": 0,
            },
        }


def upload_to_gcs(data: dict[str, Any]) -> bool:
    """Upload data to Google Cloud Storage"""
    try:
        bucket_name = os.getenv("BUCKET_NAME", "degen-digest-data")
        project_id = os.getenv("PROJECT_ID", "lucky-union-463615-t3")

        client = storage.Client(project=project_id)
        bucket = client.bucket(bucket_name)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Upload timestamped file
        timestamped_path = f"data/coingecko_{timestamp}.json"
        blob = bucket.blob(timestamped_path)
        blob.upload_from_string(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type="application/json",
        )

        # Upload latest file
        latest_path = "data/coingecko_latest.json"
        blob = bucket.blob(latest_path)
        blob.upload_from_string(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type="application/json",
        )

        logger.info(f"✅ Uploaded to GCS: {timestamped_path} and {latest_path}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to upload to GCS: {e}")
        return False


@functions_framework.http
def enhanced_coingecko_crawler(request):
    """Cloud Function handler for Enhanced CoinGecko crawler"""
    try:
        logger.info("🚀 Starting Enhanced CoinGecko Cloud Function...")

        # Crawl CoinGecko data
        data = crawl_coingecko()

        # Upload to GCS
        if upload_to_gcs(data):
            logger.info("✅ Enhanced CoinGecko Cloud Function completed successfully")
            return {
                "status": "success",
                "message": "Enhanced CoinGecko crawl completed",
                "data_count": len(data.get("coins", [])),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            logger.error("❌ Failed to upload CoinGecko data")
            return {
                "status": "error",
                "message": "Failed to upload data",
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"❌ Enhanced CoinGecko Cloud Function failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }
