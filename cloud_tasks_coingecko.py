#!/usr/bin/env python3
"""
Enhanced CoinGecko Cloud Task Handler - Focused on Viral Content
Deployed as Cloud Function or Cloud Run service
"""
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Add current directory to path
sys.path.append(".")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def crawl_coingecko() -> dict[str, Any]:
    """Enhanced CoinGecko crawl focused on viral content and opportunities"""
    try:
        logger.info("🔄 Starting Enhanced CoinGecko crawl for viral content...")

        from datetime import UTC

        import requests

        # CoinGecko API base URL
        base_url = "https://api.coingecko.com/api/v3"

        # Enhanced endpoints for viral content
        endpoints = [
            # Trending coins (most viral)
            "/search/trending",
            # Top gainers (potential viral content)
            "/coins/markets?vs_currency=usd&order=price_change_percentage_24h_desc&per_page=50&page=1&sparkline=false&price_change_percentage=1h,24h,7d",
            # New coins (launchpad opportunities)
            "/coins/markets?vs_currency=usd&order=created_desc&per_page=50&page=1&sparkline=false",
            # Solana ecosystem coins
            "/coins/markets?vs_currency=usd&ids=solana,bonk,dogwifhat,samoyedcoin,marinade,jito,tensor,raydium,orca,serum,jupiter,pyth&order=market_cap_desc&per_page=50&page=1&sparkline=false",
            # Memecoin category
            "/coins/markets?vs_currency=usd&category=meme-token&order=market_cap_desc&per_page=50&page=1&sparkline=false",
            # DeFi category (farming opportunities)
            "/coins/markets?vs_currency=usd&category=decentralized-finance-defi&order=market_cap_desc&per_page=50&page=1&sparkline=false",
            # Gaming category (potential airdrops)
            "/coins/markets?vs_currency=usd&category=gaming&order=market_cap_desc&per_page=50&page=1&sparkline=false",
            # Exchange tokens (potential airdrops)
            "/coins/markets?vs_currency=usd&category=exchange-based-tokens&order=market_cap_desc&per_page=50&page=1&sparkline=false",
        ]

        all_coins = []
        category_stats = {}

        for endpoint in endpoints:
            try:
                logger.info(f"  📊 Fetching: {endpoint[:50]}...")

                url = f"{base_url}{endpoint}"
                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    if endpoint == "/search/trending":
                        # Handle trending endpoint
                        trending_coins = data.get("coins", [])
                        for coin in trending_coins:
                            item = coin.get("item", {})
                            enhanced_coin = {
                                "id": item.get("id"),
                                "symbol": item.get("symbol", "").upper(),
                                "name": item.get("name"),
                                "market_cap_rank": item.get("market_cap_rank"),
                                "price_btc": item.get("price_btc"),
                                "score": item.get("score"),
                                "source": "coingecko",
                                "category": "trending",
                                "collected_at": datetime.now(UTC).isoformat(),
                                "viral_potential": {
                                    "keywords": extract_viral_keywords(
                                        item.get("name", "")
                                        + " "
                                        + str(item.get("symbol", ""))
                                    ),
                                    "sentiment": analyze_sentiment(
                                        item.get("name", "")
                                        + " "
                                        + str(item.get("symbol", ""))
                                    ),
                                    "urgency": detect_urgency(
                                        item.get("name", "")
                                        + " "
                                        + str(item.get("symbol", ""))
                                    ),
                                    "trending_score": item.get("score", 0),
                                },
                            }
                            all_coins.append(enhanced_coin)

                        category_stats["trending"] = len(trending_coins)
                        logger.info(f"  ✅ Trending: {len(trending_coins)} coins")

                    else:
                        # Handle market data endpoints
                        coins = data if isinstance(data, list) else []

                        for coin in coins:
                            # Enhanced coin data structure
                            enhanced_coin = {
                                "id": coin.get("id"),
                                "symbol": coin.get("symbol", "").upper(),
                                "name": coin.get("name"),
                                "current_price": coin.get("current_price"),
                                "market_cap": coin.get("market_cap"),
                                "market_cap_rank": coin.get("market_cap_rank"),
                                "total_volume": coin.get("total_volume"),
                                "high_24h": coin.get("high_24h"),
                                "low_24h": coin.get("low_24h"),
                                "price_change_24h": coin.get("price_change_24h"),
                                "price_change_percentage_24h": coin.get(
                                    "price_change_percentage_24h"
                                ),
                                "price_change_percentage_1h_in_currency": coin.get(
                                    "price_change_percentage_1h_in_currency"
                                ),
                                "price_change_percentage_7d_in_currency": coin.get(
                                    "price_change_percentage_7d_in_currency"
                                ),
                                "circulating_supply": coin.get("circulating_supply"),
                                "total_supply": coin.get("total_supply"),
                                "max_supply": coin.get("max_supply"),
                                "ath": coin.get("ath"),
                                "ath_change_percentage": coin.get(
                                    "ath_change_percentage"
                                ),
                                "ath_date": coin.get("ath_date"),
                                "atl": coin.get("atl"),
                                "atl_change_percentage": coin.get(
                                    "atl_change_percentage"
                                ),
                                "atl_date": coin.get("atl_date"),
                                "last_updated": coin.get("last_updated"),
                                "image": coin.get("image"),
                                "source": "coingecko",
                                "category": determine_category(endpoint, coin),
                                "collected_at": datetime.now(UTC).isoformat(),
                                "viral_potential": {
                                    "keywords": extract_viral_keywords(
                                        coin.get("name", "")
                                        + " "
                                        + str(coin.get("symbol", ""))
                                    ),
                                    "sentiment": analyze_sentiment(
                                        coin.get("name", "")
                                        + " "
                                        + str(coin.get("symbol", ""))
                                    ),
                                    "urgency": detect_urgency(
                                        coin.get("name", "")
                                        + " "
                                        + str(coin.get("symbol", ""))
                                    ),
                                    "price_momentum": calculate_momentum(coin),
                                    "volume_momentum": calculate_volume_momentum(coin),
                                },
                            }

                            all_coins.append(enhanced_coin)

                        # Update category stats
                        category = determine_category(endpoint, {})
                        if category not in category_stats:
                            category_stats[category] = 0
                        category_stats[category] += len(coins)

                        logger.info(f"  ✅ {category}: {len(coins)} coins")

                else:
                    logger.warning(
                        f"  ⚠️ HTTP {response.status_code} for {endpoint[:30]}..."
                    )

            except Exception as e:
                logger.error(f"  ❌ Error fetching {endpoint[:30]}...: {e}")

        # Remove duplicates based on coin ID
        seen_ids = set()
        unique_coins = []
        for coin in all_coins:
            if coin["id"] not in seen_ids:
                seen_ids.add(coin["id"])
                unique_coins.append(coin)

        data = {
            "coins": unique_coins,
            "metadata": {
                "source": "coingecko",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "success",
                "total_coins": len(unique_coins),
                "endpoints_processed": len(endpoints),
                "categories": category_stats,
                "api_source": "coingecko.com",
                "viral_content_focus": True,
            },
        }

        logger.info(
            f"✅ Enhanced CoinGecko crawl completed: {len(unique_coins)} unique coins from {len(endpoints)} endpoints"
        )
        logger.info(f"📊 Category breakdown: {category_stats}")
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


def determine_category(endpoint: str, coin: dict) -> str:
    """Determine category based on endpoint and coin data"""
    if "trending" in endpoint:
        return "trending"
    elif "meme-token" in endpoint:
        return "memecoin"
    elif "decentralized-finance-defi" in endpoint:
        return "farming"
    elif "gaming" in endpoint:
        return "gaming"
    elif "exchange-based-tokens" in endpoint:
        return "exchange"
    elif "solana" in endpoint or "bonk" in endpoint or "dogwifhat" in endpoint:
        return "solana"
    elif "created_desc" in endpoint:
        return "launchpad"
    elif "price_change_percentage_24h_desc" in endpoint:
        return "gainers"
    else:
        return "general"


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


def calculate_momentum(coin: dict) -> str:
    """Calculate price momentum based on price changes"""
    try:
        price_24h = coin.get("price_change_percentage_24h", 0)
        price_1h = coin.get("price_change_percentage_1h_in_currency", 0)
        price_7d = coin.get("price_change_percentage_7d_in_currency", 0)

        if price_24h > 50 and price_1h > 10:
            return "explosive"
        elif price_24h > 20 and price_1h > 5:
            return "strong"
        elif price_24h > 10:
            return "moderate"
        elif price_24h > 0:
            return "weak"
        else:
            return "negative"
    except:
        return "unknown"


def calculate_volume_momentum(coin: dict) -> str:
    """Calculate volume momentum"""
    try:
        volume = coin.get("total_volume", 0)
        market_cap = coin.get("market_cap", 1)

        # Volume to market cap ratio
        volume_ratio = volume / market_cap if market_cap > 0 else 0

        if volume_ratio > 0.5:
            return "very_high"
        elif volume_ratio > 0.2:
            return "high"
        elif volume_ratio > 0.1:
            return "moderate"
        else:
            return "low"
    except:
        return "unknown"


def upload_to_gcs(data: dict[str, Any]) -> bool:
    """Upload data to Google Cloud Storage"""
    try:
        from google.cloud import storage

        bucket_name = "degen-digest-data"
        project_id = "lucky-union-463615-t3"

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


def coingecko_task_handler(request):
    """Cloud Function handler for CoinGecko task"""
    try:
        logger.info("🚀 Starting Enhanced CoinGecko Cloud Task...")

        # Crawl CoinGecko data
        data = crawl_coingecko()

        # Upload to GCS
        if upload_to_gcs(data):
            logger.info("✅ Enhanced CoinGecko Cloud Task completed successfully")
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
        logger.error(f"❌ Enhanced CoinGecko Cloud Task failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# For Cloud Run compatibility
def coingecko_cloud_run(request):
    """Cloud Run handler for CoinGecko task"""
    return coingecko_task_handler(request)


# Flask app for Cloud Run
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def handle_request():
    """Handle HTTP requests for Cloud Run"""
    if request.method == "GET":
        return jsonify({"status": "healthy", "service": "enhanced-coingecko-crawler"})
    elif request.method == "POST":
        result = coingecko_task_handler(request)
        return jsonify(result)


if __name__ == "__main__":
    # For local testing
    if os.getenv("PORT"):
        # Cloud Run environment
        port = int(os.getenv("PORT", 8080))
        app.run(host="0.0.0.0", port=port)
    else:
        # Local testing
        result = coingecko_task_handler(None)
        print(json.dumps(result, indent=2))
