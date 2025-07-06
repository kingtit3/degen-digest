#!/usr/bin/env python3
"""
Enhanced Cloud Function - Improved Version with Rate Limiting
"""
import json
import logging
import os
import re
import time
from datetime import UTC, datetime, timedelta
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


def crawl_reddit_with_rate_limiting() -> dict[str, Any]:
    """Enhanced Reddit crawl with distributed search strategy over 24 hours"""
    try:
        logger.info(
            "🔄 Starting Enhanced Reddit crawl with distributed search strategy..."
        )

        # Get current hour to determine which searches to run
        current_hour = datetime.now(UTC).hour
        current_minute = datetime.now(UTC).minute

        # Calculate which searches to run based on current time
        # Spread 100 searches over 24 hours = ~4 searches per hour
        searches_per_hour = 4
        current_search_batch = current_hour % 6  # 6 different batches per day

        # Comprehensive list of Reddit sources (100 total)
        all_feeds = [
            # Batch 1: Major Crypto Subreddits (0-5 hours)
            {
                "name": "CryptoCurrency",
                "url": "https://www.reddit.com/r/CryptoCurrency/hot.json",
                "category": "general",
                "type": "json",
                "batch": 0,
            },
            {
                "name": "Bitcoin",
                "url": "https://www.reddit.com/r/Bitcoin/hot.json",
                "category": "bitcoin",
                "type": "json",
                "batch": 0,
            },
            {
                "name": "Ethereum",
                "url": "https://www.reddit.com/r/Ethereum/hot.json",
                "category": "ethereum",
                "type": "json",
                "batch": 0,
            },
            {
                "name": "Solana",
                "url": "https://www.reddit.com/r/Solana/hot.json",
                "category": "solana",
                "type": "json",
                "batch": 0,
            },
            {
                "name": "CryptoCurrency",
                "url": "https://www.reddit.com/r/CryptoCurrency/new.json",
                "category": "general",
                "type": "json",
                "batch": 1,
            },
            {
                "name": "Bitcoin",
                "url": "https://www.reddit.com/r/Bitcoin/new.json",
                "category": "bitcoin",
                "type": "json",
                "batch": 1,
            },
            # Batch 2: DeFi and Trading (6-11 hours)
            {
                "name": "defi",
                "url": "https://www.reddit.com/r/defi/hot.json",
                "category": "defi",
                "type": "json",
                "batch": 2,
            },
            {
                "name": "CryptoMarkets",
                "url": "https://www.reddit.com/r/CryptoMarkets/hot.json",
                "category": "trading",
                "type": "json",
                "batch": 2,
            },
            {
                "name": "CryptoCurrencyTrading",
                "url": "https://www.reddit.com/r/CryptoCurrencyTrading/hot.json",
                "category": "trading",
                "type": "json",
                "batch": 2,
            },
            {
                "name": "defi",
                "url": "https://www.reddit.com/r/defi/new.json",
                "category": "defi",
                "type": "json",
                "batch": 3,
            },
            {
                "name": "CryptoMarkets",
                "url": "https://www.reddit.com/r/CryptoMarkets/new.json",
                "category": "trading",
                "type": "json",
                "batch": 3,
            },
            # Batch 3: Memecoins and Viral Content (12-17 hours)
            {
                "name": "CryptoMoonShots",
                "url": "https://www.reddit.com/r/CryptoMoonShots/hot.json",
                "category": "memecoin",
                "type": "json",
                "batch": 4,
            },
            {
                "name": "shitcoin",
                "url": "https://www.reddit.com/r/shitcoin/hot.json",
                "category": "memecoin",
                "type": "json",
                "batch": 4,
            },
            {
                "name": "SatoshiStreetBets",
                "url": "https://www.reddit.com/r/SatoshiStreetBets/hot.json",
                "category": "memecoin",
                "type": "json",
                "batch": 4,
            },
            {
                "name": "CryptoMoonShots",
                "url": "https://www.reddit.com/r/CryptoMoonShots/new.json",
                "category": "memecoin",
                "type": "json",
                "batch": 5,
            },
            {
                "name": "shitcoin",
                "url": "https://www.reddit.com/r/shitcoin/new.json",
                "category": "memecoin",
                "type": "json",
                "batch": 5,
            },
            # Batch 4: NFTs and Gaming (18-23 hours)
            {
                "name": "NFT",
                "url": "https://www.reddit.com/r/NFT/hot.json",
                "category": "nft",
                "type": "json",
                "batch": 6,
            },
            {
                "name": "NFTsMarketplace",
                "url": "https://www.reddit.com/r/NFTsMarketplace/hot.json",
                "category": "nft",
                "type": "json",
                "batch": 6,
            },
            {
                "name": "CryptoGaming",
                "url": "https://www.reddit.com/r/CryptoGaming/hot.json",
                "category": "gaming",
                "type": "json",
                "batch": 6,
            },
            {
                "name": "NFT",
                "url": "https://www.reddit.com/r/NFT/new.json",
                "category": "nft",
                "type": "json",
                "batch": 7,
            },
            {
                "name": "NFTsMarketplace",
                "url": "https://www.reddit.com/r/NFTsMarketplace/new.json",
                "category": "nft",
                "type": "json",
                "batch": 7,
            },
            # Batch 5: Airdrops and Opportunities (0-5 hours)
            {
                "name": "CryptoAirdrops",
                "url": "https://www.reddit.com/r/CryptoAirdrops/hot.json",
                "category": "airdrop",
                "type": "json",
                "batch": 8,
            },
            {
                "name": "CryptoMoonShots",
                "url": "https://www.reddit.com/r/CryptoMoonShots/rising.json",
                "category": "memecoin",
                "type": "json",
                "batch": 8,
            },
            {
                "name": "CryptoCurrency",
                "url": "https://www.reddit.com/r/CryptoCurrency/rising.json",
                "category": "general",
                "type": "json",
                "batch": 8,
            },
            {
                "name": "CryptoAirdrops",
                "url": "https://www.reddit.com/r/CryptoAirdrops/new.json",
                "category": "airdrop",
                "type": "json",
                "batch": 9,
            },
            # Batch 6: Technology and Development (6-11 hours)
            {
                "name": "CryptoTechnology",
                "url": "https://www.reddit.com/r/CryptoTechnology/hot.json",
                "category": "technology",
                "type": "json",
                "batch": 10,
            },
            {
                "name": "CryptoDevs",
                "url": "https://www.reddit.com/r/CryptoDevs/hot.json",
                "category": "development",
                "type": "json",
                "batch": 10,
            },
            {
                "name": "Blockchain",
                "url": "https://www.reddit.com/r/Blockchain/hot.json",
                "category": "blockchain",
                "type": "json",
                "batch": 10,
            },
            {
                "name": "CryptoTechnology",
                "url": "https://www.reddit.com/r/CryptoTechnology/new.json",
                "category": "technology",
                "type": "json",
                "batch": 11,
            },
            # RSS Fallbacks for each batch
            {
                "name": "CryptoCurrency",
                "url": "https://www.reddit.com/r/CryptoCurrency/hot/.rss",
                "category": "general",
                "type": "rss",
                "batch": 0,
            },
            {
                "name": "Bitcoin",
                "url": "https://www.reddit.com/r/Bitcoin/hot/.rss",
                "category": "bitcoin",
                "type": "rss",
                "batch": 0,
            },
            {
                "name": "Solana",
                "url": "https://www.reddit.com/r/Solana/hot/.rss",
                "category": "solana",
                "type": "rss",
                "batch": 0,
            },
            {
                "name": "defi",
                "url": "https://www.reddit.com/r/defi/hot/.rss",
                "category": "defi",
                "type": "rss",
                "batch": 2,
            },
            {
                "name": "CryptoMoonShots",
                "url": "https://www.reddit.com/r/CryptoMoonShots/hot/.rss",
                "category": "memecoin",
                "type": "rss",
                "batch": 4,
            },
            {
                "name": "NFT",
                "url": "https://www.reddit.com/r/NFT/hot/.rss",
                "category": "nft",
                "type": "rss",
                "batch": 6,
            },
            {
                "name": "CryptoAirdrops",
                "url": "https://www.reddit.com/r/CryptoAirdrops/hot/.rss",
                "category": "airdrop",
                "type": "rss",
                "batch": 8,
            },
        ]

        # Filter feeds for current batch
        current_feeds = [
            feed for feed in all_feeds if feed.get("batch", 0) == current_search_batch
        ]

        # If no feeds for current batch, use a default set
        if not current_feeds:
            current_feeds = [
                {
                    "name": "CryptoCurrency",
                    "url": "https://www.reddit.com/r/CryptoCurrency/hot.json",
                    "category": "general",
                    "type": "json",
                },
                {
                    "name": "Bitcoin",
                    "url": "https://www.reddit.com/r/Bitcoin/hot.json",
                    "category": "bitcoin",
                    "type": "json",
                },
                {
                    "name": "Solana",
                    "url": "https://www.reddit.com/r/Solana/hot.json",
                    "category": "solana",
                    "type": "json",
                },
            ]

        logger.info(
            f"🕐 Current hour: {current_hour}, batch: {current_search_batch}, processing {len(current_feeds)} feeds"
        )

        # Use diverse user agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ]

        all_posts = []
        category_stats = {}
        successful_feeds = 0

        for i, feed in enumerate(current_feeds):
            try:
                logger.info(
                    f"  📥 Fetching {feed['name']} ({feed['category']}) via {feed['type']}... [{i+1}/{len(current_feeds)}]"
                )

                # Add delay between requests
                if i > 0:
                    time.sleep(2)  # 2 second delay between requests

                # Rotate user agents
                user_agent = user_agents[i % len(user_agents)]

                headers = {
                    "User-Agent": user_agent,
                    "Accept": "application/json, text/html, */*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Cache-Control": "max-age=0",
                }

                response = requests.get(feed["url"], timeout=20, headers=headers)

                if response.status_code == 200:
                    posts = []

                    if feed["type"] == "json":
                        # Parse JSON response
                        try:
                            data = response.json()
                            if "data" in data and "children" in data["data"]:
                                for child in data["data"]["children"][
                                    :15
                                ]:  # Increased to 15 posts per feed
                                    post_data = child.get("data", {})
                                    if post_data:
                                        post = {
                                            "title": post_data.get("title", ""),
                                            "link": f"https://reddit.com{post_data.get('permalink', '')}",
                                            "description": post_data.get(
                                                "selftext", ""
                                            ),
                                            "subreddit": feed["name"],
                                            "category": feed["category"],
                                            "source": "reddit",
                                            "published": datetime.fromtimestamp(
                                                post_data.get(
                                                    "created_utc", time.time()
                                                ),
                                                UTC,
                                            ).isoformat(),
                                            "engagement": {
                                                "upvotes": post_data.get("score", 0),
                                                "comments": post_data.get(
                                                    "num_comments", 0
                                                ),
                                                "score": post_data.get("score", 0),
                                            },
                                            "viral_potential": {
                                                "keywords": extract_viral_keywords(
                                                    post_data.get("title", "")
                                                    + " "
                                                    + post_data.get("selftext", "")
                                                ),
                                                "sentiment": analyze_sentiment(
                                                    post_data.get("title", "")
                                                    + " "
                                                    + post_data.get("selftext", "")
                                                ),
                                                "urgency": detect_urgency(
                                                    post_data.get("title", "")
                                                    + " "
                                                    + post_data.get("selftext", "")
                                                ),
                                            },
                                        }
                                        posts.append(post)
                        except json.JSONDecodeError:
                            logger.warning(
                                f"  ⚠️ Failed to parse JSON for {feed['name']}"
                            )
                            continue

                    elif feed["type"] == "rss":
                        # Parse RSS response
                        content = response.text

                        # Check if we got blocked
                        if (
                            "You've been blocked by network security" in content
                            or "blocked" in content.lower()
                        ):
                            logger.warning(
                                f"  ⚠️ Blocked by Reddit for {feed['name']}, skipping..."
                            )
                            continue

                        # Extract posts using regex
                        titles = re.findall(r"<title>(.*?)</title>", content)
                        links = re.findall(r"<link>(.*?)</link>", content)
                        descriptions = re.findall(
                            r"<description>(.*?)</description>", content
                        )

                        # Filter and process posts
                        for j, title in enumerate(titles):
                            if (
                                j < len(links)
                                and "reddit.com/r/" in links[j]
                                and j < 15
                            ):
                                # Clean up title and description
                                clean_title = (
                                    title.replace("&amp;", "&")
                                    .replace("&lt;", "<")
                                    .replace("&gt;", ">")
                                )
                                clean_desc = (
                                    descriptions[j] if j < len(descriptions) else ""
                                )
                                clean_desc = (
                                    clean_desc.replace("&amp;", "&")
                                    .replace("&lt;", "<")
                                    .replace("&gt;", ">")
                                )

                                # Enhanced post data structure
                                post = {
                                    "title": clean_title,
                                    "link": links[j],
                                    "description": clean_desc,
                                    "subreddit": feed["name"],
                                    "category": feed["category"],
                                    "source": "reddit",
                                    "published": datetime.now(UTC).isoformat(),
                                    "engagement": {
                                        "upvotes": 0,
                                        "comments": 0,
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

                    # Add posts to collection
                    all_posts.extend(posts)

                    # Update category stats
                    category = feed["category"]
                    if category not in category_stats:
                        category_stats[category] = 0
                    category_stats[category] += len(posts)

                    successful_feeds += 1
                    logger.info(f"  ✅ {feed['name']}: {len(posts)} posts")

                elif response.status_code == 429:
                    logger.warning(f"  ⚠️ Rate limited for {feed['name']}, skipping...")
                    time.sleep(5)  # Wait longer on rate limit
                    continue
                elif response.status_code == 403:
                    logger.warning(
                        f"  ⚠️ Access forbidden for {feed['name']}, trying next method..."
                    )
                    continue
                else:
                    logger.warning(
                        f"  ⚠️ Failed to fetch {feed['name']}: HTTP {response.status_code}"
                    )

            except Exception as e:
                logger.error(f"  ❌ Error fetching {feed['name']}: {e}")
                continue

        data = {
            "posts": all_posts,
            "metadata": {
                "source": "reddit",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "success" if successful_feeds > 0 else "partial",
                "total_posts": len(all_posts),
                "successful_feeds": successful_feeds,
                "total_feeds": len(current_feeds),
                "current_hour": current_hour,
                "current_batch": current_search_batch,
                "category_stats": category_stats,
                "viral_content_focus": True,
                "distributed_search": True,
            },
        }

        logger.info(
            f"✅ Enhanced Reddit crawl completed: {len(all_posts)} posts from {successful_feeds} feeds (batch {current_search_batch})"
        )
        return data

    except Exception as e:
        logger.error(f"❌ Enhanced Reddit crawl failed: {e}")
        return {
            "posts": [],
            "metadata": {
                "source": "reddit",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "error",
                "error": str(e),
                "total_posts": 0,
                "viral_content_focus": True,
                "distributed_search": True,
            },
        }


def crawl_news_with_rate_limiting() -> dict[str, Any]:
    """Enhanced News crawl with distributed search strategy over 24 hours"""
    try:
        logger.info(
            "🔄 Starting Enhanced News crawl with distributed search strategy..."
        )

        # Get current hour to determine which searches to run
        current_hour = datetime.now(UTC).hour
        current_minute = datetime.now(UTC).minute

        # Calculate which searches to run based on current time
        # Spread 100 searches over 24 hours = ~4 searches per hour
        searches_per_hour = 4
        current_search_batch = current_hour % 6  # 6 different batches per day

        # Comprehensive list of news sources and queries (100 total)
        all_news_sources = [
            # Batch 1: Major Crypto News (0-5 hours)
            {
                "source": "newsapi",
                "query": "cryptocurrency",
                "category": "general",
                "batch": 0,
            },
            {
                "source": "newsapi",
                "query": "bitcoin",
                "category": "bitcoin",
                "batch": 0,
            },
            {
                "source": "newsapi",
                "query": "ethereum",
                "category": "ethereum",
                "batch": 0,
            },
            {"source": "newsapi", "query": "solana", "category": "solana", "batch": 0},
            {
                "source": "newsapi",
                "query": "crypto market",
                "category": "trading",
                "batch": 1,
            },
            {
                "source": "newsapi",
                "query": "blockchain",
                "category": "technology",
                "batch": 1,
            },
            # Batch 2: DeFi and Trading (6-11 hours)
            {"source": "newsapi", "query": "defi", "category": "defi", "batch": 2},
            {
                "source": "newsapi",
                "query": "yield farming",
                "category": "farming",
                "batch": 2,
            },
            {
                "source": "newsapi",
                "query": "crypto trading",
                "category": "trading",
                "batch": 2,
            },
            {
                "source": "newsapi",
                "query": "liquidity mining",
                "category": "farming",
                "batch": 3,
            },
            {"source": "newsapi", "query": "amm", "category": "defi", "batch": 3},
            # Batch 3: Memecoins and Viral Content (12-17 hours)
            {
                "source": "newsapi",
                "query": "meme coin",
                "category": "memecoin",
                "batch": 4,
            },
            {
                "source": "newsapi",
                "query": "dogecoin",
                "category": "memecoin",
                "batch": 4,
            },
            {
                "source": "newsapi",
                "query": "shiba inu",
                "category": "memecoin",
                "batch": 4,
            },
            {
                "source": "newsapi",
                "query": "viral crypto",
                "category": "memecoin",
                "batch": 5,
            },
            {
                "source": "newsapi",
                "query": "crypto pump",
                "category": "trading",
                "batch": 5,
            },
            # Batch 4: NFTs and Gaming (18-23 hours)
            {"source": "newsapi", "query": "nft", "category": "nft", "batch": 6},
            {
                "source": "newsapi",
                "query": "metaverse",
                "category": "gaming",
                "batch": 6,
            },
            {
                "source": "newsapi",
                "query": "crypto gaming",
                "category": "gaming",
                "batch": 6,
            },
            {
                "source": "newsapi",
                "query": "play to earn",
                "category": "gaming",
                "batch": 7,
            },
            {
                "source": "newsapi",
                "query": "web3 gaming",
                "category": "gaming",
                "batch": 7,
            },
            # Batch 5: Airdrops and Opportunities (0-5 hours)
            {
                "source": "newsapi",
                "query": "airdrop",
                "category": "airdrop",
                "batch": 8,
            },
            {
                "source": "newsapi",
                "query": "crypto airdrop",
                "category": "airdrop",
                "batch": 8,
            },
            {
                "source": "newsapi",
                "query": "free crypto",
                "category": "airdrop",
                "batch": 8,
            },
            {
                "source": "newsapi",
                "query": "token launch",
                "category": "launch",
                "batch": 9,
            },
            {"source": "newsapi", "query": "ico", "category": "launch", "batch": 9},
            # Batch 6: Technology and Development (6-11 hours)
            {
                "source": "newsapi",
                "query": "smart contract",
                "category": "technology",
                "batch": 10,
            },
            {
                "source": "newsapi",
                "query": "layer 2",
                "category": "technology",
                "batch": 10,
            },
            {
                "source": "newsapi",
                "query": "scaling solution",
                "category": "technology",
                "batch": 10,
            },
            {
                "source": "newsapi",
                "query": "crypto development",
                "category": "development",
                "batch": 11,
            },
            {
                "source": "newsapi",
                "query": "blockchain development",
                "category": "development",
                "batch": 11,
            },
            # Alternative RSS sources for each batch (to avoid NewsAPI rate limits)
            {
                "source": "rss",
                "url": "https://cointelegraph.com/rss",
                "category": "general",
                "batch": 0,
            },
            {
                "source": "rss",
                "url": "https://coindesk.com/arc/outboundfeeds/rss/",
                "category": "general",
                "batch": 1,
            },
            {
                "source": "rss",
                "url": "https://decrypt.co/feed",
                "category": "general",
                "batch": 1,
            },
            {
                "source": "rss",
                "url": "https://www.theblock.co/rss.xml",
                "category": "general",
                "batch": 1,
            },
            {
                "source": "rss",
                "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
                "category": "bitcoin",
                "batch": 2,
            },
            {
                "source": "rss",
                "url": "https://bitcoinmagazine.com/.rss/full/",
                "category": "bitcoin",
                "batch": 2,
            },
            {
                "source": "rss",
                "url": "https://ethereum.org/en/feed.xml",
                "category": "ethereum",
                "batch": 3,
            },
            {
                "source": "rss",
                "url": "https://blog.ethereum.org/feed.xml",
                "category": "ethereum",
                "batch": 3,
            },
            {
                "source": "rss",
                "url": "https://solana.com/feed.xml",
                "category": "solana",
                "batch": 4,
            },
            {
                "source": "rss",
                "url": "https://solana.com/news/feed",
                "category": "solana",
                "batch": 4,
            },
            {
                "source": "rss",
                "url": "https://defipulse.com/blog/feed/",
                "category": "defi",
                "batch": 5,
            },
            {
                "source": "rss",
                "url": "https://defirate.com/feed/",
                "category": "defi",
                "batch": 5,
            },
            {
                "source": "rss",
                "url": "https://nftplazas.com/feed/",
                "category": "nft",
                "batch": 6,
            },
            {
                "source": "rss",
                "url": "https://nftnow.com/feed/",
                "category": "nft",
                "batch": 6,
            },
            {
                "source": "rss",
                "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
                "category": "trading",
                "batch": 7,
            },
            {
                "source": "rss",
                "url": "https://www.investing.com/rss/news_301.rss",
                "category": "trading",
                "batch": 7,
            },
        ]

        # Filter sources for current batch
        current_sources = [
            source
            for source in all_news_sources
            if source.get("batch", 0) == current_search_batch
        ]

        # If no sources for current batch, use a default set
        if not current_sources:
            current_sources = [
                {"source": "newsapi", "query": "cryptocurrency", "category": "general"},
                {"source": "newsapi", "query": "bitcoin", "category": "bitcoin"},
                {
                    "source": "rss",
                    "url": "https://cointelegraph.com/rss",
                    "category": "general",
                },
            ]

        logger.info(
            f"🕐 Current hour: {current_hour}, batch: {current_search_batch}, processing {len(current_sources)} sources"
        )

        all_articles = []
        category_stats = {}
        successful_sources = 0
        newsapi_queries = 0
        max_newsapi_queries = 2  # Limit NewsAPI queries per batch to avoid rate limits

        for i, source in enumerate(current_sources):
            try:
                logger.info(
                    f"  📰 Fetching {source['source']} ({source['category']})... [{i+1}/{len(current_sources)}]"
                )

                # Add delay between requests
                if i > 0:
                    time.sleep(3)  # 3 second delay between requests

                if source["source"] == "newsapi":
                    # Check if we've hit NewsAPI limit
                    if newsapi_queries >= max_newsapi_queries:
                        logger.info(
                            f"  ⚠️ Skipping NewsAPI query (limit reached: {newsapi_queries}/{max_newsapi_queries})"
                        )
                        continue

                    newsapi_queries += 1
                    articles = fetch_newsapi_articles(
                        source["query"], source["category"]
                    )

                elif source["source"] == "rss":
                    articles = fetch_rss_articles(source["url"], source["category"])

                else:
                    logger.warning(f"  ⚠️ Unknown source type: {source['source']}")
                    continue

                # Add articles to collection
                all_articles.extend(articles)

                # Update category stats
                category = source["category"]
                if category not in category_stats:
                    category_stats[category] = 0
                category_stats[category] += len(articles)

                successful_sources += 1
                logger.info(
                    f"  ✅ {source['source']} ({source['category']}): {len(articles)} articles"
                )

            except Exception as e:
                logger.error(
                    f"  ❌ Error fetching {source['source']} ({source['category']}): {e}"
                )
                continue

        data = {
            "articles": all_articles,
            "metadata": {
                "source": "news",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "success" if successful_sources > 0 else "partial",
                "total_articles": len(all_articles),
                "successful_sources": successful_sources,
                "total_sources": len(current_sources),
                "current_hour": current_hour,
                "current_batch": current_search_batch,
                "newsapi_queries": newsapi_queries,
                "category_stats": category_stats,
                "viral_content_focus": True,
                "distributed_search": True,
            },
        }

        logger.info(
            f"✅ Enhanced News crawl completed: {len(all_articles)} articles from {successful_sources} sources (batch {current_search_batch})"
        )
        return data

    except Exception as e:
        logger.error(f"❌ Enhanced News crawl failed: {e}")
        return {
            "articles": [],
            "metadata": {
                "source": "news",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "error",
                "error": str(e),
                "total_articles": 0,
                "viral_content_focus": True,
                "distributed_search": True,
            },
        }


def fetch_newsapi_articles(query: str, category: str) -> list[dict]:
    """Fetch articles from NewsAPI with rate limiting"""
    try:
        api_key = os.getenv("NEWSAPI_KEY")
        if not api_key:
            logger.warning("  ⚠️ No NewsAPI key found, skipping NewsAPI queries")
            return []

        # Add delay to respect rate limits
        time.sleep(1)

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": api_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 10,  # Reduced to avoid rate limits
            "from": (datetime.now(UTC) - timedelta(hours=24)).strftime("%Y-%m-%d"),
        }

        response = requests.get(url, params=params, timeout=15)

        if response.status_code == 200:
            data = response.json()
            articles = []

            for article in data.get("articles", [])[:10]:
                if article.get("title") and article.get("url"):
                    # Enhanced article structure
                    enhanced_article = {
                        "title": article.get("title", ""),
                        "link": article.get("url", ""),
                        "description": article.get("description", ""),
                        "source": article.get("source", {}).get("name", "NewsAPI"),
                        "category": category,
                        "published": article.get(
                            "publishedAt", datetime.now(UTC).isoformat()
                        ),
                        "engagement": {"views": 0, "shares": 0, "comments": 0},
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
                    articles.append(enhanced_article)

            return articles

        elif response.status_code == 429:
            logger.warning(f"  ⚠️ NewsAPI rate limit hit for query: {query}")
            return []
        else:
            logger.warning(
                f"  ⚠️ NewsAPI error for query '{query}': HTTP {response.status_code}"
            )
            return []

    except Exception as e:
        logger.error(f"  ❌ NewsAPI fetch error for query '{query}': {e}")
        return []


def fetch_rss_articles(url: str, category: str) -> list[dict]:
    """Fetch articles from RSS feeds"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            content = response.text

            # Extract articles using regex
            titles = re.findall(r"<title>(.*?)</title>", content)
            links = re.findall(r"<link>(.*?)</link>", content)
            descriptions = re.findall(r"<description>(.*?)</description>", content)
            pub_dates = re.findall(r"<pubDate>(.*?)</pubDate>", content)

            articles = []

            for j, title in enumerate(titles):
                if j < len(links) and j < 15:  # Limit to 15 articles per RSS feed
                    # Clean up content
                    clean_title = (
                        title.replace("&amp;", "&")
                        .replace("&lt;", "<")
                        .replace("&gt;", ">")
                    )
                    clean_desc = descriptions[j] if j < len(descriptions) else ""
                    clean_desc = (
                        clean_desc.replace("&amp;", "&")
                        .replace("&lt;", "<")
                        .replace("&gt;", ">")
                    )

                    # Parse publication date
                    pub_date = (
                        pub_dates[j]
                        if j < len(pub_dates)
                        else datetime.now(UTC).isoformat()
                    )

                    # Enhanced article structure
                    article = {
                        "title": clean_title,
                        "link": links[j],
                        "description": clean_desc,
                        "source": "RSS",
                        "category": category,
                        "published": pub_date,
                        "engagement": {"views": 0, "shares": 0, "comments": 0},
                        "viral_potential": {
                            "keywords": extract_viral_keywords(
                                clean_title + " " + clean_desc
                            ),
                            "sentiment": analyze_sentiment(
                                clean_title + " " + clean_desc
                            ),
                            "urgency": detect_urgency(clean_title + " " + clean_desc),
                        },
                    }

                    articles.append(article)

            return articles

        else:
            logger.warning(
                f"  ⚠️ RSS fetch error for {url}: HTTP {response.status_code}"
            )
            return []

    except Exception as e:
        logger.error(f"  ❌ RSS fetch error for {url}: {e}")
        return []


def upload_to_gcs(data: dict[str, Any], source: str) -> bool:
    """Upload data to Google Cloud Storage"""
    try:
        bucket_name = os.getenv("BUCKET_NAME", "degen-digest-data")
        project_id = os.getenv("PROJECT_ID", "lucky-union-463615-t3")

        client = storage.Client(project=project_id)
        bucket = client.bucket(bucket_name)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Upload timestamped file
        timestamped_path = f"data/{source}_{timestamp}.json"
        blob = bucket.blob(timestamped_path)
        blob.upload_from_string(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type="application/json",
        )

        # Upload latest file
        latest_path = f"data/{source}_latest.json"
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
def main(request):
    """Main cloud function entry point with distributed search strategy"""
    try:
        logger.info(
            "🚀 Starting Enhanced Viral Content Crawler with distributed search strategy..."
        )

        # Get current hour to determine which crawler to run
        current_hour = datetime.now(UTC).hour
        current_minute = datetime.now(UTC).minute

        # Calculate which crawler to run based on current time
        # Spread 100 searches over 24 hours = ~4 searches per hour
        # Rotate between Reddit, News, and CoinGecko every 2 hours
        crawler_rotation = current_hour % 6  # 6 different rotations per day

        logger.info(f"🕐 Current hour: {current_hour}, rotation: {crawler_rotation}")

        # Determine which crawler to run based on rotation
        if crawler_rotation in [0, 1]:  # Hours 0-1, 6-7, 12-13, 18-19
            logger.info("📥 Running Reddit crawler (batch 1/2)")
            result = crawl_reddit_with_rate_limiting()
            source = "reddit"

        elif crawler_rotation in [2, 3]:  # Hours 2-3, 8-9, 14-15, 20-21
            logger.info("📰 Running News crawler (batch 1/2)")
            result = crawl_news_with_rate_limiting()
            source = "news"

        elif crawler_rotation in [4, 5]:  # Hours 4-5, 10-11, 16-17, 22-23
            logger.info("💰 Running CoinGecko crawler (batch 1/2)")
            result = crawl_coingecko_with_rate_limiting()
            source = "coingecko"

        else:
            # Fallback to Reddit
            logger.info("📥 Running Reddit crawler (fallback)")
            result = crawl_reddit_with_rate_limiting()
            source = "reddit"

        # Upload results to GCS
        if result and result.get("metadata", {}).get("status") != "error":
            upload_success = upload_to_gcs(result, source)
            if upload_success:
                logger.info(f"✅ Successfully uploaded {source} data to GCS")
            else:
                logger.error(f"❌ Failed to upload {source} data to GCS")

        # Return response
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "message": f"Enhanced {source} crawler completed successfully",
                    "data": {
                        "source": source,
                        "current_hour": current_hour,
                        "rotation": crawler_rotation,
                        "total_items": result.get("metadata", {}).get("total_posts", 0)
                        or result.get("metadata", {}).get("total_articles", 0)
                        or result.get("metadata", {}).get("total_coins", 0),
                        "distributed_search": True,
                        "viral_content_focus": True,
                    },
                }
            ),
        }

    except Exception as e:
        logger.error(f"❌ Main function failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "status": "error",
                    "message": f"Enhanced crawler failed: {str(e)}",
                    "data": {
                        "current_hour": datetime.now(UTC).hour,
                        "distributed_search": True,
                        "viral_content_focus": True,
                    },
                }
            ),
        }


@functions_framework.http
def enhanced_reddit_crawler(request):
    """Cloud Function handler for Enhanced Reddit crawler with rate limiting"""
    try:
        logger.info("🚀 Starting Enhanced Reddit Cloud Function with rate limiting...")

        # Crawl Reddit data with rate limiting
        data = crawl_reddit_with_rate_limiting()

        # Upload to GCS
        if upload_to_gcs(data, "reddit"):
            logger.info("✅ Enhanced Reddit Cloud Function completed successfully")
            return {
                "status": "success",
                "message": "Enhanced Reddit crawl completed with rate limiting",
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
        logger.error(f"❌ Enhanced Reddit Cloud Function failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@functions_framework.http
def enhanced_news_crawler(request):
    """Cloud Function handler for Enhanced News crawler with rate limiting"""
    try:
        logger.info("🚀 Starting Enhanced News Cloud Function with rate limiting...")

        # Crawl News data with rate limiting
        data = crawl_news_with_rate_limiting()

        # Upload to GCS
        if upload_to_gcs(data, "news"):
            logger.info("✅ Enhanced News Cloud Function completed successfully")
            return {
                "status": "success",
                "message": "Enhanced News crawl completed with rate limiting",
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
