#!/usr/bin/env python3
"""
Enhanced News Cloud Function - Standalone Version
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


def crawl_news() -> dict[str, Any]:
    """Enhanced News crawl focused on viral content sources"""
    try:
        logger.info("🔄 Starting Enhanced News crawl for viral content...")

        api_key = os.getenv("NEWSAPI_KEY", "ffc45af6fcd94c4991eaefdc469346e8")

        # Enhanced search queries focused on viral content
        queries = [
            # Memecoin & Viral Content
            "memecoin pump moon",
            "cryptocurrency viral trending",
            "solana memecoin launch",
            "bonk dogwifhat solana",
            "pepe doge shib floki",
            # Launchpads & IDOs
            "crypto launchpad presale",
            "token launch ico ido",
            "fair launch stealth launch",
            "pinksale dxsale bounce",
            # Airdrops
            "crypto airdrop claim",
            "token distribution free",
            "retroactive airdrop",
            "community airdrop",
            # Farming & Yield
            "yield farming defi",
            "liquidity mining staking",
            "apy apr rewards",
            "defi farming strategy",
            # Solana Ecosystem
            "solana ecosystem development",
            "phantom solflare raydium",
            "jupiter pyth tensor",
            "magic eden saga",
            # Trading & Markets
            "crypto market pump dump",
            "bitcoin ethereum price",
            "altcoin season bull run",
            "crypto whale movement",
            # General Crypto
            "cryptocurrency news breaking",
            "blockchain technology update",
            "defi protocol launch",
            "nft marketplace trending",
        ]

        all_articles = []
        query_stats = {}

        for query in queries:
            try:
                logger.info(f"  📥 Fetching news for: {query}...")

                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": query,
                    "apiKey": api_key,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 20,  # Get more articles per query
                    "from": datetime.now().strftime("%Y-%m-%d"),  # Today's articles
                }

                response = requests.get(url, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])

                    # Process articles
                    processed_articles = []
                    for article in articles:
                        if article.get("title") and article.get("url"):
                            # Enhanced article data structure
                            processed_article = {
                                "title": article.get("title", ""),
                                "description": article.get("description", ""),
                                "url": article.get("url", ""),
                                "source": article.get("source", {}).get(
                                    "name", "Unknown"
                                ),
                                "published": article.get("publishedAt", ""),
                                "content": article.get("content", ""),
                                "query": query,
                                "source_type": "news",
                                "engagement": {
                                    "relevance_score": 0,  # Will be calculated
                                    "viral_potential": 0,
                                },
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
                                },
                            }

                            processed_articles.append(processed_article)

                    # Limit to top 10 articles per query for viral content
                    all_articles.extend(processed_articles[:10])

                    # Update query stats
                    query_stats[query] = len(processed_articles[:10])

                    logger.info(f"  ✅ {query}: {len(processed_articles)} articles")
                else:
                    logger.warning(
                        f"  ⚠️ Failed to fetch {query}: HTTP {response.status_code}"
                    )

            except Exception as e:
                logger.error(f"  ❌ Error fetching {query}: {e}")

        data = {
            "articles": all_articles,
            "metadata": {
                "source": "news",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "success",
                "total_articles": len(all_articles),
                "queries": list(query_stats.keys()),
                "query_stats": query_stats,
                "queries_processed": len(queries),
                "viral_content_focus": True,
            },
        }

        logger.info(
            f"✅ Enhanced News crawl completed: {len(all_articles)} articles from {len(queries)} queries"
        )
        logger.info(f"📊 Query breakdown: {query_stats}")
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


def upload_to_gcs(data: dict[str, Any]) -> bool:
    """Upload data to Google Cloud Storage"""
    try:
        bucket_name = os.getenv("BUCKET_NAME", "degen-digest-data")
        project_id = os.getenv("PROJECT_ID", "lucky-union-463615-t3")

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


@functions_framework.http
def enhanced_news_crawler(request):
    """Cloud Function handler for Enhanced News crawler"""
    try:
        logger.info("🚀 Starting Enhanced News Cloud Function...")

        # Crawl News data
        data = crawl_news()

        # Upload to GCS
        if upload_to_gcs(data):
            logger.info("✅ Enhanced News Cloud Function completed successfully")
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
        logger.error(f"❌ Enhanced News Cloud Function failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }
