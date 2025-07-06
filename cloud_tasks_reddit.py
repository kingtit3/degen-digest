#!/usr/bin/env python3
"""
Enhanced Reddit Cloud Task Handler - Focused on Viral Content
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


def crawl_reddit() -> dict[str, Any]:
    """Enhanced Reddit crawl focused on viral content sources"""
    try:
        logger.info("🔄 Starting Enhanced Reddit crawl for viral content...")

        import re
        from datetime import UTC

        import requests

        # Enhanced Reddit RSS feeds focused on viral content
        feeds = [
            # Memecoin & Viral Content
            {
                "name": "CryptoMoonShots",
                "url": "https://www.reddit.com/r/CryptoMoonShots/new/.rss",
                "category": "memecoin",
            },
            {
                "name": "CryptoCurrency",
                "url": "https://www.reddit.com/r/CryptoCurrency/new/.rss",
                "category": "general",
            },
            {
                "name": "shitcoin",
                "url": "https://www.reddit.com/r/shitcoin/new/.rss",
                "category": "memecoin",
            },
            {
                "name": "cryptocurrencymemes",
                "url": "https://www.reddit.com/r/cryptocurrencymemes/new/.rss",
                "category": "memecoin",
            },
            {
                "name": "cryptomemes",
                "url": "https://www.reddit.com/r/cryptomemes/new/.rss",
                "category": "memecoin",
            },
            # Solana Ecosystem
            {
                "name": "Solana",
                "url": "https://www.reddit.com/r/Solana/new/.rss",
                "category": "solana",
            },
            {
                "name": "SolanaNFTs",
                "url": "https://www.reddit.com/r/SolanaNFTs/new/.rss",
                "category": "solana",
            },
            {
                "name": "SolanaDeFi",
                "url": "https://www.reddit.com/r/SolanaDeFi/new/.rss",
                "category": "solana",
            },
            # Launchpads & IDOs
            {
                "name": "launchpad",
                "url": "https://www.reddit.com/r/launchpad/new/.rss",
                "category": "launchpad",
            },
            {
                "name": "IDO",
                "url": "https://www.reddit.com/r/IDO/new/.rss",
                "category": "launchpad",
            },
            {
                "name": "presale",
                "url": "https://www.reddit.com/r/presale/new/.rss",
                "category": "launchpad",
            },
            # Airdrops
            {
                "name": "airdrop",
                "url": "https://www.reddit.com/r/airdrop/new/.rss",
                "category": "airdrop",
            },
            {
                "name": "CryptoAirdrops",
                "url": "https://www.reddit.com/r/CryptoAirdrops/new/.rss",
                "category": "airdrop",
            },
            # Farming & Yield
            {
                "name": "defi",
                "url": "https://www.reddit.com/r/defi/new/.rss",
                "category": "farming",
            },
            {
                "name": "yieldfarming",
                "url": "https://www.reddit.com/r/yieldfarming/new/.rss",
                "category": "farming",
            },
            {
                "name": "liquiditymining",
                "url": "https://www.reddit.com/r/liquiditymining/new/.rss",
                "category": "farming",
            },
            # Trading & Signals
            {
                "name": "cryptotrading",
                "url": "https://www.reddit.com/r/cryptotrading/new/.rss",
                "category": "trading",
            },
            {
                "name": "cryptosignals",
                "url": "https://www.reddit.com/r/cryptosignals/new/.rss",
                "category": "trading",
            },
            {
                "name": "CryptoMarkets",
                "url": "https://www.reddit.com/r/CryptoMarkets/new/.rss",
                "category": "trading",
            },
            # General Crypto
            {
                "name": "Bitcoin",
                "url": "https://www.reddit.com/r/Bitcoin/new/.rss",
                "category": "general",
            },
            {
                "name": "Ethereum",
                "url": "https://www.reddit.com/r/Ethereum/new/.rss",
                "category": "general",
            },
            {
                "name": "altcoin",
                "url": "https://www.reddit.com/r/altcoin/new/.rss",
                "category": "general",
            },
            {
                "name": "cryptonews",
                "url": "https://www.reddit.com/r/cryptonews/new/.rss",
                "category": "general",
            },
            {
                "name": "ethtrader",
                "url": "https://www.reddit.com/r/ethtrader/new/.rss",
                "category": "general",
            },
            {
                "name": "NFT",
                "url": "https://www.reddit.com/r/NFT/new/.rss",
                "category": "general",
            },
        ]

        all_posts = []
        category_stats = {}

        for feed in feeds:
            try:
                logger.info(f"  📥 Fetching {feed['name']} ({feed['category']})...")
                response = requests.get(feed["url"], timeout=15)

                if response.status_code == 200:
                    content = response.text

                    # Extract posts using regex
                    titles = re.findall(r"<title>(.*?)</title>", content)
                    links = re.findall(r"<link>(.*?)</link>", content)
                    descriptions = re.findall(
                        r"<description>(.*?)</description>", content
                    )

                    # Filter and process posts
                    posts = []
                    for i, title in enumerate(titles):
                        if i < len(links) and "reddit.com/r/" in links[i]:
                            # Clean up title and description
                            clean_title = (
                                title.replace("&amp;", "&")
                                .replace("&lt;", "<")
                                .replace("&gt;", ">")
                            )
                            clean_desc = (
                                descriptions[i] if i < len(descriptions) else ""
                            )
                            clean_desc = (
                                clean_desc.replace("&amp;", "&")
                                .replace("&lt;", "<")
                                .replace("&gt;", ">")
                            )

                            # Enhanced post data structure
                            post = {
                                "title": clean_title,
                                "link": links[i],
                                "description": clean_desc,
                                "subreddit": feed["name"],
                                "category": feed["category"],
                                "source": "reddit",
                                "published": datetime.now(UTC).isoformat(),
                                "engagement": {
                                    "upvotes": 0,  # RSS doesn't provide this
                                    "comments": 0,  # RSS doesn't provide this
                                    "score": 0,
                                },
                                "viral_potential": {
                                    "keywords": extract_viral_keywords(
                                        clean_title + " " + clean_desc
                                    ),
                                    "sentiment": analyze_sentiment(
                                        clean_title + " " + clean_desc
                                    ),
                                    "urgency": detect_urgency(
                                        clean_title + " " + clean_desc
                                    ),
                                },
                            }

                            posts.append(post)

                    # Limit to top 15 posts per subreddit for viral content
                    all_posts.extend(posts[:15])

                    # Update category stats
                    category = feed["category"]
                    if category not in category_stats:
                        category_stats[category] = 0
                    category_stats[category] += len(posts[:15])

                    logger.info(f"  ✅ {feed['name']}: {len(posts)} posts")
                else:
                    logger.warning(
                        f"  ⚠️ Failed to fetch {feed['name']}: HTTP {response.status_code}"
                    )

            except Exception as e:
                logger.error(f"  ❌ Error fetching {feed['name']}: {e}")

        data = {
            "posts": all_posts,
            "metadata": {
                "source": "reddit",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "success",
                "total_posts": len(all_posts),
                "subreddits": [feed["name"] for feed in feeds],
                "categories": category_stats,
                "feeds_processed": len(feeds),
                "viral_content_focus": True,
            },
        }

        logger.info(
            f"✅ Enhanced Reddit crawl completed: {len(all_posts)} posts from {len(feeds)} subreddits"
        )
        logger.info(f"📊 Category breakdown: {category_stats}")
        return data

    except Exception as e:
        logger.error(f"❌ Enhanced Reddit crawl failed: {e}")
        return {
            "posts": [],
            "metadata": {
                "source": "reddit",
                "crawled_at": datetime.now().isoformat(),
                "status": "error",
                "error": str(e),
                "total_posts": 0,
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
        timestamped_path = f"data/reddit_{timestamp}.json"
        blob = bucket.blob(timestamped_path)
        blob.upload_from_string(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type="application/json",
        )

        # Upload latest file
        latest_path = "data/reddit_latest.json"
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


def reddit_task_handler(request):
    """Cloud Function handler for Reddit task"""
    try:
        logger.info("🚀 Starting Enhanced Reddit Cloud Task...")

        # Crawl Reddit data
        data = crawl_reddit()

        # Upload to GCS
        if upload_to_gcs(data):
            logger.info("✅ Enhanced Reddit Cloud Task completed successfully")
            return {
                "status": "success",
                "message": "Enhanced Reddit crawl completed",
                "data_count": len(data.get("posts", [])),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            logger.error("❌ Failed to upload Reddit data")
            return {
                "status": "error",
                "message": "Failed to upload data",
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"❌ Enhanced Reddit Cloud Task failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# For Cloud Run compatibility
def reddit_cloud_run(request):
    """Cloud Run handler for Reddit task"""
    return reddit_task_handler(request)


# Flask app for Cloud Run
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def handle_request():
    """Handle HTTP requests for Cloud Run"""
    if request.method == "GET":
        return jsonify({"status": "healthy", "service": "enhanced-reddit-crawler"})
    elif request.method == "POST":
        result = reddit_task_handler(request)
        return jsonify(result)


if __name__ == "__main__":
    # For local testing
    if os.getenv("PORT"):
        # Cloud Run environment
        port = int(os.getenv("PORT", 8080))
        app.run(host="0.0.0.0", port=port)
    else:
        # Local testing
        result = reddit_task_handler(None)
        print(json.dumps(result, indent=2))
