#!/usr/bin/env python3
"""
Enhanced News Cloud Task Handler - Focused on Viral Content
Deployed as Cloud Function or Cloud Run service
"""
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict

# Add current directory to path
sys.path.append(".")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def crawl_news() -> dict[str, Any]:
    """Enhanced news crawl focused on viral content and crypto opportunities"""
    try:
        logger.info("🔄 Starting Enhanced News crawl for viral content...")

        from datetime import UTC

        import requests

        # Get NewsAPI key from environment
        newsapi_key = os.getenv("NEWSAPI_KEY")
        if not newsapi_key:
            logger.error("❌ NEWSAPI_KEY not found in environment variables")
            return {
                "articles": [],
                "metadata": {
                    "source": "news",
                    "crawled_at": datetime.now(UTC).isoformat(),
                    "status": "error",
                    "error": "NEWSAPI_KEY not configured",
                    "total_articles": 0,
                },
            }

        # Enhanced crypto-related search queries focused on viral content
        queries = [
            # Memecoin & Viral Content
            "memecoin OR meme coin OR pepe OR doge OR shib OR floki OR bonk OR dogwifhat",
            "moon OR pump OR 100x OR 1000x OR gem OR next gem OR viral crypto",
            "wen OR ser OR ngmi OR wagmi OR gm OR based OR chad OR degen",
            # Launchpads & IDOs
            "launchpad OR ido OR initial dex offering OR token launch OR presale",
            "fair launch OR stealth launch OR pinksale OR dxsale OR bounce",
            "polkastarter OR daomaker OR trustpad OR seedify OR gamefi",
            "new token OR ico OR initial coin offering OR whitelist OR kyc",
            # Airdrops
            "airdrop OR free tokens OR claim OR eligibility OR snapshot",
            "whitelist OR retroactive OR community airdrop OR token distribution",
            "free crypto OR claim now OR don't miss out",
            # Farming & Yield
            "yield farming OR farming OR liquidity mining OR staking OR apy OR apr",
            "rewards OR harvest OR compound OR auto compound OR vault OR strategy",
            "defi farming OR liquidity provider OR lp OR amm OR dex farming",
            "impermanent loss OR yield optimizer",
            # Solana Ecosystem
            "solana OR sol OR phantom OR solflare OR raydium OR orca OR serum",
            "jupiter OR pyth OR bonk OR dogwifhat OR samoyedcoin OR marinade",
            "jito OR tensor OR magic eden OR saga OR firedancer OR solana mobile",
            "solana pay OR spl OR spl token",
            # General Crypto Trends
            "crypto OR cryptocurrency OR bitcoin OR ethereum OR blockchain",
            "defi OR nft OR web3 OR metaverse OR gaming crypto",
            "altcoin OR alt season OR bull run OR bear market",
            # Breaking News & Urgency
            "breaking crypto OR urgent OR live OR now OR today OR deadline",
            "crypto news OR crypto update OR crypto announcement",
            "crypto regulation OR crypto adoption OR institutional crypto",
        ]

        all_articles = []
        category_stats = {}

        for query in queries:
            try:
                logger.info(f"  📰 Fetching news for: {query[:50]}...")

                # NewsAPI endpoint
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": query,
                    "apiKey": newsapi_key,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 20,  # Increased for more comprehensive coverage
                    "from": (datetime.now() - timedelta(days=2)).strftime(
                        "%Y-%m-%d"
                    ),  # Last 2 days
                }

                response = requests.get(url, params=params, timeout=20)

                if response.status_code == 200:
                    data = response.json()

                    if data.get("status") == "ok":
                        articles = data.get("articles", [])

                        for article in articles:
                            # Clean and structure article data
                            clean_article = {
                                "title": article.get("title", ""),
                                "description": article.get("description", ""),
                                "content": article.get("content", ""),
                                "url": article.get("url", ""),
                                "source": article.get("source", {}).get("name", ""),
                                "author": article.get("author", ""),
                                "published_at": article.get("publishedAt", ""),
                                "query": query,
                                "source_type": "news",
                                "collected_at": datetime.now(UTC).isoformat(),
                                "viral_potential": {
                                    "keywords": extract_viral_keywords(
                                        article.get("title", "")
                                        + " "
                                        + article.get("description", "")
                                    ),
                                    "sentiment": analyze_sentiment(
                                        article.get("title", "")
                                        + " "
                                        + article.get("description", "")
                                    ),
                                    "urgency": detect_urgency(
                                        article.get("title", "")
                                        + " "
                                        + article.get("description", "")
                                    ),
                                    "category": categorize_article(
                                        article.get("title", "")
                                        + " "
                                        + article.get("description", "")
                                    ),
                                },
                            }

                            all_articles.append(clean_article)

                        # Update category stats
                        category = categorize_article(query)
                        if category not in category_stats:
                            category_stats[category] = 0
                        category_stats[category] += len(articles)

                        logger.info(f"  ✅ {query[:30]}...: {len(articles)} articles")
                    else:
                        logger.warning(
                            f"  ⚠️ NewsAPI error for {query[:30]}...: {data.get('message', 'Unknown error')}"
                        )
                else:
                    logger.warning(
                        f"  ⚠️ HTTP {response.status_code} for {query[:30]}..."
                    )

            except Exception as e:
                logger.error(f"  ❌ Error fetching news for {query[:30]}...: {e}")

        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                unique_articles.append(article)

        data = {
            "articles": unique_articles,
            "metadata": {
                "source": "news",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "success",
                "total_articles": len(unique_articles),
                "queries_processed": len(queries),
                "categories": category_stats,
                "api_source": "newsapi.org",
                "viral_content_focus": True,
            },
        }

        logger.info(
            f"✅ Enhanced News crawl completed: {len(unique_articles)} unique articles from {len(queries)} queries"
        )
        logger.info(f"📊 Category breakdown: {category_stats}")
        return data

    except Exception as e:
        logger.error(f"❌ Enhanced News crawl failed: {e}")
        return {
            "articles": [],
            "metadata": {
                "source": "news",
                "crawled_at": datetime.now().isoformat(),
                "status": "error",
                "error": str(e),
                "total_articles": 0,
            },
        }


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
        # News keywords
        "announcement",
        "partnership",
        "integration",
        "launch",
        "release",
        "update",
        "upgrade",
        "migration",
        "bridge",
        "swap",
        "exchange",
        "listing",
        "delisting",
        "regulation",
        "adoption",
        "institutional",
        "enterprise",
        "mainnet",
        "testnet",
        "beta",
        "alpha",
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
        "partnership",
        "launch",
        "adoption",
        "success",
        "growth",
        "surge",
        "rally",
        "breakout",
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
        "regulation",
        "ban",
        "restriction",
        "hack",
        "exploit",
        "vulnerability",
        "bug",
        "glitch",
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
        "announcement",
        "launch",
        "release",
        "update",
        "migration",
        "snapshot",
    ]

    text_lower = text.lower()
    urgent_count = sum(1 for word in urgent_words if word in text_lower)

    if urgent_count >= 3:
        return "high"
    elif urgent_count >= 1:
        return "medium"
    else:
        return "low"


def categorize_article(text: str) -> str:
    """Categorize article based on content"""
    text_lower = text.lower()

    # Memecoin category
    memecoin_words = [
        "meme",
        "pepe",
        "doge",
        "shib",
        "floki",
        "bonk",
        "dogwifhat",
        "moon",
        "pump",
        "gem",
        "wen",
        "ser",
        "ngmi",
        "wagmi",
        "gm",
        "based",
        "chad",
        "degen",
    ]
    if any(word in text_lower for word in memecoin_words):
        return "memecoin"

    # Launchpad category
    launchpad_words = [
        "launchpad",
        "ido",
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
        "whitelist",
        "kyc",
    ]
    if any(word in text_lower for word in launchpad_words):
        return "launchpad"

    # Airdrop category
    airdrop_words = [
        "airdrop",
        "free tokens",
        "claim",
        "eligibility",
        "snapshot",
        "retroactive",
        "community airdrop",
        "token distribution",
        "free crypto",
    ]
    if any(word in text_lower for word in airdrop_words):
        return "airdrop"

    # Farming category
    farming_words = [
        "yield farming",
        "farming",
        "liquidity mining",
        "staking",
        "apy",
        "apr",
        "rewards",
        "harvest",
        "compound",
        "vault",
        "strategy",
        "defi farming",
        "liquidity provider",
        "lp",
        "amm",
        "dex farming",
    ]
    if any(word in text_lower for word in farming_words):
        return "farming"

    # Solana category
    solana_words = [
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
    ]
    if any(word in text_lower for word in solana_words):
        return "solana"

    # General crypto
    return "general"


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
        timestamped_path = f"data/news_{timestamp}.json"
        blob = bucket.blob(timestamped_path)
        blob.upload_from_string(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type="application/json",
        )

        # Upload latest file
        latest_path = "data/news_latest.json"
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


def news_task_handler(request):
    """Cloud Function handler for News task"""
    try:
        logger.info("🚀 Starting Enhanced News Cloud Task...")

        # Crawl news data
        data = crawl_news()

        # Upload to GCS
        if upload_to_gcs(data):
            logger.info("✅ Enhanced News Cloud Task completed successfully")
            return {
                "status": "success",
                "message": "Enhanced News crawl completed",
                "data_count": len(data.get("articles", [])),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            logger.error("❌ Failed to upload News data")
            return {
                "status": "error",
                "message": "Failed to upload data",
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"❌ Enhanced News Cloud Task failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# For Cloud Run compatibility
def news_cloud_run(request):
    """Cloud Run handler for News task"""
    return news_task_handler(request)


# Flask app for Cloud Run
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def handle_request():
    """Handle HTTP requests for Cloud Run"""
    if request.method == "GET":
        return jsonify({"status": "healthy", "service": "enhanced-news-crawler"})
    elif request.method == "POST":
        result = news_task_handler(request)
        return jsonify(result)


if __name__ == "__main__":
    # For local testing
    if os.getenv("PORT"):
        # Cloud Run environment
        port = int(os.getenv("PORT", 8080))
        app.run(host="0.0.0.0", port=port)
    else:
        # Local testing
        result = news_task_handler(None)
        print(json.dumps(result, indent=2))
