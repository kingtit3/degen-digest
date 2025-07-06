import json
import logging
import os
from datetime import UTC, datetime

import functions_framework
from google.cloud import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BUCKET_NAME = os.environ.get("BUCKET_NAME", "degen-digest-data")
PROJECT_ID = os.environ.get("PROJECT_ID", "lucky-union-463615-t3")


# Helper to load JSON from GCS
def load_gcs_json(blob_name):
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    if not blob.exists():
        logger.warning(f"Blob {blob_name} does not exist in bucket {BUCKET_NAME}")
        return []
    try:
        data = json.loads(blob.download_as_text())
        return data
    except Exception as e:
        logger.error(f"Failed to load {blob_name}: {e}")
        return []


# Helper to save JSON/Markdown to GCS
def save_gcs_file(blob_name, content, content_type="application/json"):
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    if content_type == "application/json":
        blob.upload_from_string(
            json.dumps(content, indent=2, ensure_ascii=False), content_type=content_type
        )
    else:
        blob.upload_from_string(content, content_type=content_type)
    logger.info(f"Saved {blob_name} to GCS")


# Viral analysis and categorization helpers (copied from enhanced_digest_generator.py, simplified)
def analyze_viral_potential(item):
    if not isinstance(item, dict):
        return {
            "viral_score": 0.0,
            "viral_factors": ["invalid item format"],
            "viral_level": "low",
        }

    viral_score = 0
    viral_factors = []
    viral_keywords = [
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
        "chad",
        "based",
        "degen",
        "mooning",
        "pumping",
        "fomo",
        "fud",
        "hodl",
        "launchpad",
        "ido",
        "airdrop",
        "presale",
        "fair launch",
        "stealth launch",
        "yield farming",
        "farming",
        "staking",
        "apy",
        "apr",
        "rewards",
        "solana",
        "sol",
        "phantom",
        "bonk",
        "dogwifhat",
        "jupiter",
        "pyth",
        "now",
        "today",
        "live",
        "breaking",
        "urgent",
        "don't miss",
        "last chance",
        "viral",
        "trending",
        "hot",
        "fire",
        "lit",
        "savage",
        "epic",
        "legendary",
    ]

    # Safely extract text content
    text = ""
    for k in ("title", "description", "text", "name"):
        if k in item and item[k]:
            text += str(item[k]) + " "

    if not text.strip():
        return {
            "viral_score": 0.0,
            "viral_factors": ["no text content"],
            "viral_level": "low",
        }

    text_lower = text.lower()

    # Count viral keywords
    keyword_count = sum(1 for keyword in viral_keywords if keyword in text_lower)
    if keyword_count > 0:
        viral_score += keyword_count * 0.1
        viral_factors.append(f"{keyword_count} viral keywords")

    # Check urgency indicators
    urgency_words = [
        "now",
        "today",
        "live",
        "breaking",
        "urgent",
        "don't miss",
        "last chance",
    ]
    urgency_count = sum(1 for word in urgency_words if word in text_lower)
    if urgency_count > 0:
        viral_score += urgency_count * 0.2
        viral_factors.append(f"{urgency_count} urgency indicators")

    # Check sentiment
    if "sentiment" in item and item["sentiment"]:
        sentiment = item["sentiment"]
        if sentiment == "positive":
            viral_score += 0.3
            viral_factors.append("positive sentiment")
        elif sentiment == "negative":
            viral_score -= 0.1
            viral_factors.append("negative sentiment")

    # Check engagement metrics
    if "engagement" in item and isinstance(item["engagement"], dict):
        engagement = item["engagement"]
        if (
            "upvotes" in engagement
            and isinstance(engagement["upvotes"], (int, float))
            and engagement["upvotes"] > 100
        ):
            viral_score += 0.2
            viral_factors.append("high engagement")
        elif (
            "likes" in engagement
            and isinstance(engagement["likes"], (int, float))
            and engagement["likes"] > 50
        ):
            viral_score += 0.15
            viral_factors.append("good engagement")

    # Check price movement for market data
    if "price_change_percentage_24h" in item:
        try:
            change = float(item["price_change_percentage_24h"])
            if change > 20:
                viral_score += 0.4
                viral_factors.append("strong price movement")
            elif change > 10:
                viral_score += 0.2
                viral_factors.append("moderate price movement")
        except (ValueError, TypeError):
            pass

    # Ensure viral score is within bounds
    viral_score = max(0.0, min(viral_score, 1.0))

    # Determine viral level
    if viral_score > 0.5:
        viral_level = "high"
    elif viral_score > 0.2:
        viral_level = "medium"
    else:
        viral_level = "low"

    return {
        "viral_score": viral_score,
        "viral_factors": viral_factors,
        "viral_level": viral_level,
    }


def categorize_content(item):
    if not isinstance(item, dict):
        return "general"

    # Safely extract text content
    text = ""
    for k in ("title", "description", "text", "name"):
        if k in item and item[k]:
            text += str(item[k]) + " "

    if not text.strip():
        return "general"

    text_lower = text.lower()

    # Define keyword categories
    memecoin_keywords = [
        "pepe",
        "doge",
        "shib",
        "floki",
        "wojak",
        "bonk",
        "dogwifhat",
        "moon",
        "pump",
        "gem",
    ]
    if any(keyword in text_lower for keyword in memecoin_keywords):
        return "memecoin"

    defi_keywords = [
        "defi",
        "yield farming",
        "farming",
        "staking",
        "apy",
        "apr",
        "liquidity",
        "amm",
        "dex",
    ]
    if any(keyword in text_lower for keyword in defi_keywords):
        return "defi"

    nft_keywords = ["nft", "non-fungible", "opensea", "magic eden", "tensor", "jupiter"]
    if any(keyword in text_lower for keyword in nft_keywords):
        return "nft"

    solana_keywords = [
        "solana",
        "sol",
        "phantom",
        "solflare",
        "raydium",
        "orca",
        "serum",
        "jupiter",
        "pyth",
    ]
    if any(keyword in text_lower for keyword in solana_keywords):
        return "solana"

    launchpad_keywords = [
        "launchpad",
        "ido",
        "presale",
        "fair launch",
        "stealth launch",
        "whitelist",
    ]
    if any(keyword in text_lower for keyword in launchpad_keywords):
        return "launchpad"

    airdrop_keywords = ["airdrop", "claim", "eligibility", "snapshot", "free tokens"]
    if any(keyword in text_lower for keyword in airdrop_keywords):
        return "airdrop"

    bitcoin_keywords = ["bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain"]
    if any(keyword in text_lower for keyword in bitcoin_keywords):
        return "bitcoin_ethereum"

    return "general"


# Markdown generator
def generate_markdown_digest(digest_data):
    metadata = digest_data["metadata"]
    content = digest_data["content"]
    markdown = f"""# 🚀 Enhanced Degen Digest - {datetime.now().strftime('%Y-%m-%d')}
\n## 📊 Executive Summary\nGenerated on: {metadata['generated_at']}\nTotal items analyzed: {metadata['total_items']}\nViral content items: {metadata['viral_content_count']}\nSources: {', '.join(metadata['sources'])}\nCategories: {', '.join(metadata['categories'])}\n\n## 🔥 Top Viral Content\n\n"""
    for i, item in enumerate(content["top_viral"][:10], 1):
        viral_score = item["viral_analysis"]["viral_score"]
        viral_factors = ", ".join(item["viral_analysis"]["viral_factors"])
        if item["source"] == "reddit":
            markdown += f"### {i}. 🚀 {item['title'][:100]}...\n- **Viral Score:** {viral_score:.2f}\n- **Viral Factors:** {viral_factors}\n- **Subreddit:** r/{item['subreddit']}\n- **Category:** {item['category']}\n- **Link:** {item['link']}\n\n"
        elif item["source"] == "news":
            markdown += f"### {i}. 📰 {item['title'][:100]}...\n- **Viral Score:** {viral_score:.2f}\n- **Viral Factors:** {viral_factors}\n- **Source:** {item.get('source_name','')}\n- **Category:** {item['category']}\n- **Link:** {item['link']}\n\n"
        elif item["source"] == "coingecko":
            markdown += f"### {i}. 💰 {item['name']} ({item['symbol']})\n- **Viral Score:** {viral_score:.2f}\n- **Viral Factors:** {viral_factors}\n- **Price:** ${item['price']}\n- **24h Change:** {item['price_change_24h']:.2f}%\n- **Category:** {item['category']}\n\n"
        elif item["source"] == "twitter":
            markdown += f"### {i}. 🐦 {item['text'][:100]}...\n- **Viral Score:** {viral_score:.2f}\n- **Viral Factors:** {viral_factors}\n- **User:** @{item['user']}\n- **Category:** {item['category']}\n\n"
    markdown += "\n## 📈 Category Breakdown\n\n"
    for category, items in content["by_category"].items():
        if items:
            markdown += f"### {category.title()}: {len(items)} items\n"
            for item in items[:3]:
                if "title" in item:
                    markdown += f"- {item['title'][:80]}...\n"
                elif "name" in item:
                    markdown += f"- {item['name']} ({item['symbol']})\n"
                elif "text" in item:
                    markdown += f"- {item['text'][:80]}...\n"
            markdown += "\n"
    markdown += """\n---\n*Generated by Enhanced Degen Digest System* 🤖\n*Viral Content Analysis Powered by AI* 🧠\n"""
    return markdown


# Main digest handler
def run_digest_generation():
    # Load all data from GCS
    reddit_data = load_gcs_json("data/reddit_latest.json")
    news_data = load_gcs_json("data/news_latest.json")
    coingecko_data = load_gcs_json("data/coingecko_latest.json")
    twitter_data = load_gcs_json("data/twitter_playwright_enhanced_latest.json")

    # Unpack with proper error handling
    reddit_posts = []
    if isinstance(reddit_data, dict) and reddit_data.get("posts"):
        reddit_posts = (
            reddit_data["posts"] if isinstance(reddit_data["posts"], list) else []
        )

    news_articles = []
    if isinstance(news_data, dict) and news_data.get("articles"):
        news_articles = (
            news_data["articles"] if isinstance(news_data["articles"], list) else []
        )

    coingecko_coins = []
    if isinstance(coingecko_data, dict) and coingecko_data.get("coins"):
        coingecko_coins = (
            coingecko_data["coins"] if isinstance(coingecko_data["coins"], list) else []
        )

    twitter_tweets = []
    if isinstance(twitter_data, dict) and twitter_data.get("tweets"):
        twitter_tweets = (
            twitter_data["tweets"] if isinstance(twitter_data["tweets"], list) else []
        )

    logger.info(
        f"Loaded data: Reddit={len(reddit_posts)}, News={len(news_articles)}, Coingecko={len(coingecko_coins)}, Twitter={len(twitter_tweets)}"
    )

    # Process all items
    all_items = []

    # Process Reddit posts
    for post in reddit_posts:
        if not isinstance(post, dict):
            logger.warning(f"Skipping non-dict reddit post: {type(post)}")
            continue
        try:
            viral_analysis = analyze_viral_potential(post)
            category = categorize_content(post)
            processed_post = {
                "id": post.get("id", f"reddit_{len(all_items)}"),
                "title": post.get("title", ""),
                "description": post.get("description", ""),
                "link": post.get("link", ""),
                "source": "reddit",
                "subreddit": post.get("subreddit", ""),
                "category": category,
                "viral_analysis": viral_analysis,
                "published": post.get("published", datetime.now(UTC).isoformat()),
                "engagement": post.get("engagement", {}),
                "sentiment": post.get("sentiment", "neutral"),
            }
            all_items.append(processed_post)
        except Exception as e:
            logger.error(f"Error processing reddit post: {e}")
            continue

    # Process News articles
    for article in news_articles:
        if not isinstance(article, dict):
            logger.warning(f"Skipping non-dict news article: {type(article)}")
            continue
        try:
            viral_analysis = analyze_viral_potential(article)
            category = categorize_content(article)
            processed_article = {
                "id": article.get("id", f"news_{len(all_items)}"),
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "link": article.get("url", ""),
                "source": "news",
                "source_name": article.get("source", ""),
                "category": category,
                "viral_analysis": viral_analysis,
                "published": article.get("publishedAt", datetime.now(UTC).isoformat()),
                "sentiment": article.get("sentiment", "neutral"),
            }
            all_items.append(processed_article)
        except Exception as e:
            logger.error(f"Error processing news article: {e}")
            continue

    # Process Coingecko coins
    for coin in coingecko_coins:
        if not isinstance(coin, dict):
            logger.warning(f"Skipping non-dict coingecko coin: {type(coin)}")
            continue
        try:
            viral_analysis = analyze_viral_potential(coin)
            category = categorize_content(coin)
            processed_coin = {
                "id": coin.get("id", f"coingecko_{len(all_items)}"),
                "name": coin.get("name", ""),
                "symbol": coin.get("symbol", ""),
                "price": coin.get("current_price", 0),
                "market_cap": coin.get("market_cap", 0),
                "price_change_24h": coin.get("price_change_percentage_24h", 0),
                "source": "coingecko",
                "category": category,
                "viral_analysis": viral_analysis,
                "published": coin.get("published", datetime.now(UTC).isoformat()),
            }
            all_items.append(processed_coin)
        except Exception as e:
            logger.error(f"Error processing coingecko coin: {e}")
            continue

    # Process Twitter tweets
    for tweet in twitter_tweets:
        if not isinstance(tweet, dict):
            logger.warning(f"Skipping non-dict twitter tweet: {type(tweet)}")
            continue
        try:
            viral_analysis = analyze_viral_potential(tweet)
            category = categorize_content(tweet)
            processed_tweet = {
                "id": tweet.get("id", f"twitter_{len(all_items)}"),
                "text": tweet.get("text", ""),
                "user": tweet.get("username", ""),
                "source": "twitter",
                "category": category,
                "viral_analysis": viral_analysis,
                "published": tweet.get("created_at", datetime.now(UTC).isoformat()),
                "engagement": tweet.get(
                    "engagement", {"likes": 0, "retweets": 0, "replies": 0}
                ),
            }
            all_items.append(processed_tweet)
        except Exception as e:
            logger.error(f"Error processing twitter tweet: {e}")
            continue

    logger.info(f"Successfully processed {len(all_items)} total items")

    # Sort by viral score
    all_items.sort(key=lambda x: x["viral_analysis"]["viral_score"], reverse=True)

    # Group by category/source
    categories = {}
    for item in all_items:
        category = item["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(item)

    top_viral = [
        item for item in all_items if item["viral_analysis"]["viral_level"] == "high"
    ][:10]

    by_source = {}
    for item in all_items:
        source = item["source"]
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(item)

    digest_content = {
        "top_viral": top_viral,
        "by_category": categories,
        "by_source": by_source,
        "summary": {
            "total_items": len(all_items),
            "viral_items": len(top_viral),
            "categories": list(categories.keys()),
            "sources": list(by_source.keys()),
        },
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    digest_data = {
        "metadata": {
            "generated_at": datetime.now(UTC).isoformat(),
            "total_items": len(all_items),
            "sources": list({item["source"] for item in all_items}),
            "categories": list({item["category"] for item in all_items}),
            "viral_content_count": len(
                [
                    item
                    for item in all_items
                    if item["viral_analysis"]["viral_level"] == "high"
                ]
            ),
            "enhanced_analysis": True,
        },
        "content": digest_content,
        "items": all_items[:100],
    }

    # Save to GCS
    save_gcs_file(f"data/enhanced_digest_{timestamp}.json", digest_data)
    save_gcs_file("data/enhanced_digest_latest.json", digest_data)
    markdown_content = generate_markdown_digest(digest_data)
    save_gcs_file(
        f"data/enhanced_digest_{datetime.now().strftime('%Y-%m-%d')}.md",
        markdown_content,
        content_type="text/markdown",
    )

    logger.info(f"✅ Enhanced digest generated: {len(all_items)} items analyzed")
    return digest_data


@functions_framework.http
def enhanced_digest_cloud(request):
    """HTTP Cloud Function to generate enhanced digest from GCS data"""
    logger.info("Received request to generate enhanced digest from GCS data")
    result = run_digest_generation()
    return (
        json.dumps(
            {
                "status": "success",
                "message": "Enhanced digest generated",
                "total_items": result["metadata"]["total_items"],
            }
        ),
        200,
        {"Content-Type": "application/json"},
    )
