#!/usr/bin/env python3
"""
Enhanced Cloud Function - Fixed Version with Better RSS Parsing
"""
import json
import logging
import os
import re
import time
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


def parse_rss_content(content: str) -> list[dict]:
    """Parse RSS content and extract posts"""
    posts = []

    try:
        # Better regex patterns for RSS parsing
        # Look for <entry> tags which contain individual posts
        entry_pattern = r"<entry>(.*?)</entry>"
        entries = re.findall(entry_pattern, content, re.DOTALL)

        logger.info(f"Found {len(entries)} entries in RSS feed")

        for entry in entries:
            try:
                # Extract title
                title_match = re.search(r"<title[^>]*>(.*?)</title>", entry, re.DOTALL)
                title = title_match.group(1).strip() if title_match else ""

                # Extract link
                link_match = re.search(r'<link[^>]*href="([^"]*)"', entry)
                link = link_match.group(1) if link_match else ""

                # Extract content/summary
                content_match = re.search(
                    r"<content[^>]*>(.*?)</content>", entry, re.DOTALL
                )
                if not content_match:
                    content_match = re.search(
                        r"<summary[^>]*>(.*?)</summary>", entry, re.DOTALL
                    )
                content_text = content_match.group(1).strip() if content_match else ""

                # Clean up HTML entities
                title = (
                    title.replace("&amp;", "&")
                    .replace("&lt;", "<")
                    .replace("&gt;", ">")
                    .replace("&quot;", '"')
                )
                content_text = (
                    content_text.replace("&amp;", "&")
                    .replace("&lt;", "<")
                    .replace("&gt;", ">")
                    .replace("&quot;", '"')
                )

                if title and link and "reddit.com/r/" in link:
                    posts.append(
                        {
                            "title": title,
                            "link": link,
                            "description": content_text,
                            "published": datetime.now(UTC).isoformat(),
                        }
                    )

            except Exception as e:
                logger.warning(f"Error parsing entry: {e}")
                continue

    except Exception as e:
        logger.error(f"Error parsing RSS content: {e}")

    return posts


def crawl_reddit_fixed() -> dict[str, Any]:
    """Enhanced Reddit crawl with fixed RSS parsing"""
    try:
        logger.info("🔄 Starting Enhanced Reddit crawl with fixed parsing...")

        # Reduced list of most important subreddits
        feeds = [
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
                "name": "Solana",
                "url": "https://www.reddit.com/r/Solana/new/.rss",
                "category": "solana",
            },
            {
                "name": "defi",
                "url": "https://www.reddit.com/r/defi/new/.rss",
                "category": "farming",
            },
        ]

        all_posts = []
        category_stats = {}
        successful_feeds = 0

        for i, feed in enumerate(feeds):
            try:
                logger.info(
                    f"  📥 Fetching {feed['name']} ({feed['category']})... [{i+1}/{len(feeds)}]"
                )

                # Add delay between requests
                if i > 0:
                    time.sleep(2)

                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }

                response = requests.get(feed["url"], timeout=15, headers=headers)

                if response.status_code == 200:
                    content = response.text
                    logger.info(f"  📄 Content length: {len(content)}")

                    # Parse RSS content
                    posts = parse_rss_content(content)
                    logger.info(f"  📊 Parsed {len(posts)} posts from {feed['name']}")

                    # Process posts
                    processed_posts = []
                    for post in posts[:10]:  # Limit to top 10
                        enhanced_post = {
                            "title": post["title"],
                            "link": post["link"],
                            "description": post["description"],
                            "subreddit": feed["name"],
                            "category": feed["category"],
                            "source": "reddit",
                            "published": post["published"],
                            "engagement": {"upvotes": 0, "comments": 0, "score": 0},
                            "viral_potential": {
                                "keywords": extract_viral_keywords(
                                    post["title"] + " " + post["description"]
                                ),
                                "sentiment": analyze_sentiment(
                                    post["title"] + " " + post["description"]
                                ),
                                "urgency": detect_urgency(
                                    post["title"] + " " + post["description"]
                                ),
                            },
                        }
                        processed_posts.append(enhanced_post)

                    all_posts.extend(processed_posts)

                    # Update category stats
                    category = feed["category"]
                    if category not in category_stats:
                        category_stats[category] = 0
                    category_stats[category] += len(processed_posts)

                    successful_feeds += 1
                    logger.info(
                        f"  ✅ {feed['name']}: {len(processed_posts)} posts processed"
                    )

                elif response.status_code == 429:
                    logger.warning(f"  ⚠️ Rate limited for {feed['name']}, skipping...")
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
                "status": "success",
                "total_posts": len(all_posts),
                "subreddits": [feed["name"] for feed in feeds],
                "categories": category_stats,
                "feeds_processed": successful_feeds,
                "total_feeds": len(feeds),
                "viral_content_focus": True,
            },
        }

        logger.info(
            f"✅ Enhanced Reddit crawl completed: {len(all_posts)} posts from {successful_feeds}/{len(feeds)} subreddits"
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


def crawl_news_fixed() -> dict[str, Any]:
    """Enhanced News crawl with rate limit handling"""
    try:
        logger.info("🔄 Starting Enhanced News crawl with rate limit handling...")

        newsapi_key = os.environ.get("NEWSAPI_KEY")
        if not newsapi_key:
            logger.error("NEWSAPI_KEY not found in environment variables")
            return {
                "articles": [],
                "metadata": {
                    "source": "news",
                    "crawled_at": datetime.now().isoformat(),
                    "status": "error",
                    "error": "NEWSAPI_KEY not found",
                    "total_articles": 0,
                },
            }

        # Very limited queries to avoid rate limits
        queries = ["cryptocurrency bitcoin", "defi yield farming"]

        all_articles = []
        successful_queries = 0

        for i, query in enumerate(queries):
            try:
                logger.info(
                    f"  📥 Fetching news for: {query}... [{i+1}/{len(queries)}]"
                )

                # Add delay between requests
                if i > 0:
                    time.sleep(5)  # Longer delay for NewsAPI

                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": query,
                    "apiKey": newsapi_key,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 5,  # Very small to avoid rate limits
                    "page": 1,
                }

                response = requests.get(url, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])

                    for article in articles:
                        if article.get("title") and article.get("url"):
                            enhanced_article = {
                                "title": article.get("title", ""),
                                "description": article.get("description", ""),
                                "url": article.get("url", ""),
                                "source": article.get("source", {}).get("name", ""),
                                "publishedAt": article.get("publishedAt", ""),
                                "query": query,
                                "source": "news",
                                "published": datetime.now(UTC).isoformat(),
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
                            all_articles.append(enhanced_article)

                    successful_queries += 1
                    logger.info(f"  ✅ {query}: {len(articles)} articles")

                elif response.status_code == 429:
                    logger.warning(f"  ⚠️ Rate limited for {query}, skipping...")
                    continue
                else:
                    logger.warning(
                        f"  ⚠️ Failed to fetch {query}: HTTP {response.status_code}"
                    )

            except Exception as e:
                logger.error(f"  ❌ Error fetching {query}: {e}")
                continue

        data = {
            "articles": all_articles,
            "metadata": {
                "source": "news",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "success",
                "total_articles": len(all_articles),
                "queries": queries,
                "queries_processed": successful_queries,
                "total_queries": len(queries),
                "viral_content_focus": True,
            },
        }

        logger.info(
            f"✅ Enhanced News crawl completed: {len(all_articles)} articles from {successful_queries}/{len(queries)} queries"
        )
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
def enhanced_reddit_crawler(request):
    """Cloud Function handler for Enhanced Reddit crawler with fixed parsing"""
    try:
        logger.info("🚀 Starting Enhanced Reddit Cloud Function with fixed parsing...")

        # Crawl Reddit data with fixed parsing
        data = crawl_reddit_fixed()

        # Upload to GCS
        if upload_to_gcs(data, "reddit"):
            logger.info("✅ Enhanced Reddit Cloud Function completed successfully")
            return {
                "status": "success",
                "message": "Enhanced Reddit crawl completed with fixed parsing",
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
    """Cloud Function handler for Enhanced News crawler with rate limit handling"""
    try:
        logger.info(
            "🚀 Starting Enhanced News Cloud Function with rate limit handling..."
        )

        # Crawl News data with rate limit handling
        data = crawl_news_fixed()

        # Upload to GCS
        if upload_to_gcs(data, "news"):
            logger.info("✅ Enhanced News Cloud Function completed successfully")
            return {
                "status": "success",
                "message": "Enhanced News crawl completed with rate limit handling",
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
