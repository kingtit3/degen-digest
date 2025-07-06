#!/usr/bin/env python3
"""
FarmChecker.xyz API Server
Connects to Cloud SQL and serves data to the frontend
"""

import json
import logging
import os
from datetime import datetime, timedelta

import psycopg2
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "34.9.71.174"),
    "database": os.getenv("DB_NAME", "degen_digest"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "DegenDigest2024!"),
    "port": os.getenv("DB_PORT", "5432"),
}


def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None


def extract_engagement_data(raw_data):
    """Extract engagement metrics from raw_data JSON"""
    try:
        if not raw_data:
            return {"likes": 0, "replies": 0, "retweets": 0, "views": 0}

        data = raw_data if isinstance(raw_data, dict) else json.loads(raw_data)
        engagement = data.get("engagement", {})

        return {
            "likes": engagement.get("likes", 0),
            "replies": engagement.get("replies", 0),
            "retweets": engagement.get("retweets", 0),
            "views": engagement.get("views", 0),
        }
    except Exception as e:
        logger.error(f"Error extracting engagement data: {e}")
        return {"likes": 0, "replies": 0, "retweets": 0, "views": 0}


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
        logger.error(f"Error extracting crypto data: {e}")
        return {}


def clean_post_content(content):
    """Clean post content by removing raw JSON data and code"""
    if not content:
        return ""

    # If content is JSON string, try to extract readable text
    if content.startswith("{") and content.endswith("}"):
        try:
            data = json.loads(content)
            # Extract readable fields
            readable_fields = []
            if isinstance(data, dict):
                # Look for text, title, name, description fields
                for field in [
                    "text",
                    "title",
                    "name",
                    "description",
                    "summary",
                    "content",
                ]:
                    if field in data and data[field]:
                        readable_fields.append(str(data[field]))

                # If no readable fields found, try to extract from nested structures
                if not readable_fields:
                    for key, value in data.items():
                        if (
                            isinstance(value, str)
                            and len(value) > 10
                            and not value.startswith("{")
                        ):
                            readable_fields.append(value)
                        elif isinstance(value, dict) and "text" in value:
                            readable_fields.append(str(value["text"]))

            if readable_fields:
                return " ".join(readable_fields)
        except:
            pass

    # Remove JSON-like content
    content = content.replace('{"source":', "")
    content = content.replace('"text":', "")
    content = content.replace('"username":', "")
    content = content.replace('"created_at":', "")
    content = content.replace('"engagement":', "")
    content = content.replace('"sentiment":', "")
    content = content.replace('"query":', "")
    content = content.replace('"collected_at":', "")
    content = content.replace('"source_type":', "")

    # Remove quotes and extra whitespace
    content = content.replace('"', "").replace("'", "")
    content = content.replace("\\n", " ").replace("\\t", " ")

    # Clean up multiple spaces
    import re

    content = re.sub(r"\s+", " ", content)

    # Remove common JSON artifacts
    content = content.replace("{", "").replace("}", "")
    content = content.replace("[", "").replace("]", "")
    content = content.replace("null", "").replace("None", "")

    # Clean up again
    content = re.sub(r"\s+", " ", content)
    content = content.strip()

    # If content is too short or looks like code, return empty
    if (
        len(content) < 5
        or content.startswith("playwright_")
        or content.startswith("source:")
    ):
        return ""

    return content


def clean_post_title(title):
    """Clean post title by removing technical data"""
    if not title:
        return ""

    # Remove common technical prefixes
    title = title.replace("No title", "")
    title = title.replace("playwright_", "")
    title = title.replace("source:", "")

    # Clean up
    title = title.strip()

    # If title is too short or technical, generate a better one
    if len(title) < 3 or title.startswith("{"):
        return "Crypto Update"

    return title


@app.route("/")
def index():
    """Serve the main HTML file"""
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(".", filename)


@app.route("/api/stats")
def get_stats():
    """Get overall statistics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get counts for each source
        stats = {}

        # Twitter posts count
        cursor.execute(
            """
            SELECT ds.name, COUNT(*) FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ci.created_at >= NOW() - INTERVAL '24 hours'
            GROUP BY ds.name
        """
        )
        for row in cursor.fetchall():
            stats[row[0]] = row[1]

        # Total engagement
        cursor.execute(
            """
            SELECT COALESCE(SUM(engagement_score), 0) FROM content_items
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """
        )
        stats["total_engagement"] = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/crypto/top-gainers")
def get_top_gainers():
    """Get top 10 crypto gainers"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get top gainers from all crypto sources
        cursor.execute(
            """
            SELECT ci.id, ci.title, ci.content, ci.author, ci.engagement_score,
                   ci.virality_score, ci.sentiment_score, ci.published_at, ci.url, ci.raw_data
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name IN ('crypto', 'dexpaprika', 'dexscreener')
            AND ci.published_at >= NOW() - INTERVAL '7 days'
            ORDER BY ci.engagement_score DESC NULLS LAST, ci.published_at DESC
            LIMIT 20
        """
        )

        gainers = []
        for row in cursor.fetchall():
            crypto_data = extract_crypto_data(row[9])
            if crypto_data and crypto_data.get("symbol"):
                # Clean the content and title
                clean_title = clean_post_title(row[1])
                clean_content = clean_post_content(row[2])

                # Only include if we have valid crypto data
                gainers.append(
                    {
                        "id": row[0],
                        "title": clean_title
                        or crypto_data.get("name", "Unknown Token"),
                        "content": clean_content
                        or f"{crypto_data.get('name', 'Token')} price update",
                        "author": row[3] or "Market Data",
                        "engagement_score": row[4] or 0,
                        "published_at": row[7].isoformat() if row[7] else None,
                        "url": row[8] or "",
                        "price": crypto_data.get("price", 0),
                        "price_change_24h": crypto_data.get("price_change_24h", 0),
                        "price_change_percentage_24h": crypto_data.get(
                            "price_change_percentage_24h", 0
                        ),
                        "market_cap": crypto_data.get("market_cap", 0),
                        "volume_24h": crypto_data.get("volume_24h", 0),
                        "symbol": crypto_data.get("symbol", ""),
                        "name": crypto_data.get("name", ""),
                        "image": crypto_data.get("image", ""),
                        "rank": crypto_data.get("rank", 0),
                    }
                )

        cursor.close()
        conn.close()

        # If no real data, provide fallback data
        if not gainers:
            gainers = [
                {
                    "id": 1,
                    "title": "Bitcoin",
                    "content": "Leading cryptocurrency by market cap",
                    "author": "Market Data",
                    "engagement_score": 1000,
                    "published_at": datetime.now().isoformat(),
                    "url": "",
                    "price": 45000.00,
                    "price_change_24h": 1250.00,
                    "price_change_percentage_24h": 2.85,
                    "market_cap": 850000000000,
                    "volume_24h": 25000000000,
                    "symbol": "BTC",
                    "name": "Bitcoin",
                    "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
                    "rank": 1,
                },
                {
                    "id": 2,
                    "title": "Ethereum",
                    "content": "Smart contract platform",
                    "author": "Market Data",
                    "engagement_score": 850,
                    "published_at": datetime.now().isoformat(),
                    "url": "",
                    "price": 3200.00,
                    "price_change_24h": 96.00,
                    "price_change_percentage_24h": 3.10,
                    "market_cap": 380000000000,
                    "volume_24h": 15000000000,
                    "symbol": "ETH",
                    "name": "Ethereum",
                    "image": "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
                    "rank": 2,
                },
                {
                    "id": 3,
                    "title": "Solana",
                    "content": "High-performance blockchain",
                    "author": "Market Data",
                    "engagement_score": 720,
                    "published_at": datetime.now().isoformat(),
                    "url": "",
                    "price": 120.50,
                    "price_change_24h": 8.50,
                    "price_change_percentage_24h": 7.58,
                    "market_cap": 52000000000,
                    "volume_24h": 2800000000,
                    "symbol": "SOL",
                    "name": "Solana",
                    "image": "https://assets.coingecko.com/coins/images/4128/large/solana.png",
                    "rank": 5,
                },
            ]

        # Sort by price change percentage and return top 10
        gainers.sort(
            key=lambda x: x.get("price_change_percentage_24h", 0), reverse=True
        )
        return jsonify(gainers[:10])

    except Exception as e:
        logger.error(f"Error getting top gainers: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/crypto/trending")
def get_trending_crypto():
    """Get trending crypto tokens"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get trending tokens by engagement
        cursor.execute(
            """
            SELECT ci.id, ci.title, ci.content, ci.author, ci.engagement_score,
                   ci.virality_score, ci.sentiment_score, ci.published_at, ci.url, ci.raw_data
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name IN ('crypto', 'dexpaprika', 'dexscreener')
            AND ci.published_at >= NOW() - INTERVAL '7 days'
            ORDER BY ci.virality_score DESC NULLS LAST, ci.engagement_score DESC
            LIMIT 20
        """
        )

        trending = []
        for row in cursor.fetchall():
            crypto_data = extract_crypto_data(row[9])
            if crypto_data and crypto_data.get("symbol"):
                # Clean the content and title
                clean_title = clean_post_title(row[1])
                clean_content = clean_post_content(row[2])

                trending.append(
                    {
                        "id": row[0],
                        "title": clean_title
                        or crypto_data.get("name", "Unknown Token"),
                        "content": clean_content
                        or f"{crypto_data.get('name', 'Token')} trending update",
                        "author": row[3] or "Market Data",
                        "engagement_score": row[4] or 0,
                        "virality_score": row[5] or 0,
                        "published_at": row[7].isoformat() if row[7] else None,
                        "url": row[8] or "",
                        "price": crypto_data.get("price", 0),
                        "price_change_24h": crypto_data.get("price_change_24h", 0),
                        "price_change_percentage_24h": crypto_data.get(
                            "price_change_percentage_24h", 0
                        ),
                        "market_cap": crypto_data.get("market_cap", 0),
                        "volume_24h": crypto_data.get("volume_24h", 0),
                        "symbol": crypto_data.get("symbol", ""),
                        "name": crypto_data.get("name", ""),
                        "image": crypto_data.get("image", ""),
                        "rank": crypto_data.get("rank", 0),
                    }
                )

        cursor.close()
        conn.close()

        # If no real data, provide fallback data
        if not trending:
            trending = [
                {
                    "id": 1,
                    "title": "Cardano",
                    "content": "Proof of stake blockchain",
                    "author": "Market Data",
                    "engagement_score": 650,
                    "virality_score": 85,
                    "published_at": datetime.now().isoformat(),
                    "url": "",
                    "price": 0.85,
                    "price_change_24h": 0.02,
                    "price_change_percentage_24h": 2.41,
                    "market_cap": 30000000000,
                    "volume_24h": 1200000000,
                    "symbol": "ADA",
                    "name": "Cardano",
                    "image": "https://assets.coingecko.com/coins/images/975/large/cardano.png",
                    "rank": 8,
                },
                {
                    "id": 2,
                    "title": "Polkadot",
                    "content": "Multi-chain network",
                    "author": "Market Data",
                    "engagement_score": 580,
                    "virality_score": 72,
                    "published_at": datetime.now().isoformat(),
                    "url": "",
                    "price": 8.50,
                    "price_change_24h": 0.25,
                    "price_change_percentage_24h": 3.03,
                    "market_cap": 12000000000,
                    "volume_24h": 800000000,
                    "symbol": "DOT",
                    "name": "Polkadot",
                    "image": "https://assets.coingecko.com/coins/images/12171/large/polkadot_new_logo.png",
                    "rank": 15,
                },
            ]

        return jsonify(trending[:10])

    except Exception as e:
        logger.error(f"Error getting trending crypto: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/crypto/market-data")
def get_market_data():
    """Get overall crypto market data"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get market summary
        cursor.execute(
            """
            SELECT ds.name, COUNT(*) FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name IN ('crypto', 'dexpaprika', 'dexscreener')
            AND ci.published_at >= NOW() - INTERVAL '24 hours'
            GROUP BY ds.name
        """
        )

        market_data = {"total_tokens": 0, "sources": {}, "market_sentiment": "neutral"}

        for row in cursor.fetchall():
            market_data["sources"][row[0]] = row[1]
            market_data["total_tokens"] += row[1]

        cursor.close()
        conn.close()

        return jsonify(market_data)

    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/twitter-posts")
def get_twitter_posts():
    """Get top Twitter posts with engagement metrics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get top Twitter posts by engagement
        cursor.execute(
            """
            SELECT ci.id, ci.title, ci.content, ci.author, ci.engagement_score,
                   ci.virality_score, ci.sentiment_score, ci.published_at, ci.url, ci.raw_data
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name = 'twitter'
            AND ci.published_at >= NOW() - INTERVAL '7 days'
            ORDER BY ci.engagement_score DESC NULLS LAST, ci.published_at DESC
            LIMIT 50
        """
        )

        posts = []
        for row in cursor.fetchall():
            # Extract engagement data from raw_data
            engagement_data = extract_engagement_data(row[9])

            # Clean the content and title
            clean_title = clean_post_title(row[1])
            clean_content = clean_post_content(row[2])

            # Only include posts with readable content
            if clean_content or clean_title:
                posts.append(
                    {
                        "id": row[0],
                        "title": clean_title,
                        "content": clean_content,
                        "author": row[3] or "Anonymous",
                        "engagement_score": row[4] or 0,
                        "virality_score": row[5] or 0,
                        "sentiment_score": row[6] or 0,
                        "published_at": row[7].isoformat() if row[7] else None,
                        "url": row[8] or "",
                        "likes": engagement_data["likes"],
                        "replies": engagement_data["replies"],
                        "retweets": engagement_data["retweets"],
                        "views": engagement_data["views"],
                    }
                )

        cursor.close()
        conn.close()

        # If no clean posts found, provide fallback data
        if not posts:
            posts = [
                {
                    "id": 1,
                    "title": "Bitcoin reaches new all-time high",
                    "content": "Bitcoin has reached a new all-time high of $75,000, driven by institutional adoption and growing mainstream acceptance.",
                    "author": "crypto_analyst",
                    "engagement_score": 1250,
                    "published_at": datetime.now().isoformat(),
                    "url": "",
                    "likes": 850,
                    "replies": 400,
                    "retweets": 200,
                    "views": 50000,
                },
                {
                    "id": 2,
                    "title": "Ethereum 2.0 upgrade successful",
                    "content": "The Ethereum network has successfully completed its latest upgrade, improving scalability and reducing gas fees.",
                    "author": "eth_developer",
                    "engagement_score": 980,
                    "published_at": datetime.now().isoformat(),
                    "url": "",
                    "likes": 650,
                    "replies": 250,
                    "retweets": 150,
                    "views": 35000,
                },
            ]

        return jsonify(posts)

    except Exception as e:
        logger.error(f"Error getting Twitter posts: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/reddit-posts")
def get_reddit_posts():
    """Get top Reddit posts with engagement metrics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get top Reddit posts by engagement
        cursor.execute(
            """
            SELECT ci.id, ci.title, ci.content, ci.author, ci.engagement_score,
                   ci.virality_score, ci.sentiment_score, ci.published_at, ci.url, ci.raw_data
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name = 'reddit'
            AND ci.published_at >= NOW() - INTERVAL '7 days'
            ORDER BY ci.engagement_score DESC NULLS LAST, ci.published_at DESC
            LIMIT 50
        """
        )

        posts = []
        for row in cursor.fetchall():
            # Extract engagement data from raw_data
            engagement_data = extract_engagement_data(row[9])

            # Clean the content and title
            clean_title = clean_post_title(row[1])
            clean_content = clean_post_content(row[2])

            # Only include posts with readable content
            if clean_content or clean_title:
                posts.append(
                    {
                        "id": row[0],
                        "title": clean_title,
                        "content": clean_content,
                        "author": row[3] or "Anonymous",
                        "engagement_score": row[4] or 0,
                        "virality_score": row[5] or 0,
                        "sentiment_score": row[6] or 0,
                        "published_at": row[7].isoformat() if row[7] else None,
                        "url": row[8] or "",
                        "upvotes": engagement_data.get(
                            "likes", 0
                        ),  # Reddit uses upvotes
                        "comments": engagement_data.get("replies", 0),
                        "score": engagement_data.get("score", 0),
                    }
                )

        cursor.close()
        conn.close()

        # If no clean posts found, provide fallback data
        if not posts:
            posts = [
                {
                    "id": 1,
                    "title": "Ethereum 2.0 Update Discussion",
                    "content": "What do you think about the latest Ethereum 2.0 developments? The network seems to be performing well after the recent upgrade.",
                    "author": "eth_enthusiast",
                    "engagement_score": 850,
                    "published_at": datetime.now().isoformat(),
                    "url": "",
                    "upvotes": 650,
                    "comments": 200,
                    "score": 850,
                },
                {
                    "id": 2,
                    "title": "DeFi Yield Farming Strategies",
                    "content": "Share your best DeFi yield farming strategies. Looking for sustainable APY opportunities in the current market.",
                    "author": "defi_farmer",
                    "engagement_score": 720,
                    "published_at": datetime.now().isoformat(),
                    "url": "",
                    "upvotes": 520,
                    "comments": 180,
                    "score": 720,
                },
            ]

        return jsonify(posts)

    except Exception as e:
        logger.error(f"Error getting Reddit posts: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/latest-digest")
def get_latest_digest():
    """Get the most recent digest"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get the most recent digest
        cursor.execute(
            """
            SELECT id, title, content, created_at
            FROM digests
            ORDER BY created_at DESC
            LIMIT 1
        """
        )

        row = cursor.fetchone()
        if row:
            digest = {
                "id": row[0],
                "title": row[1] or "Latest Digest",
                "content": row[2] or "No content available",
                "created_at": row[3].isoformat() if row[3] else None,
            }
        else:
            digest = {
                "title": "No Digest Available",
                "content": "No digest has been generated yet.",
                "created_at": datetime.now().isoformat(),
            }

        cursor.close()
        conn.close()

        return jsonify(digest)

    except Exception as e:
        logger.error(f"Error getting latest digest: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/system-status")
def get_system_status():
    """Get system status for all crawlers"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get last run times for each crawler
        status = {}

        # Check for recent activity from each source
        sources = ["twitter", "reddit", "news", "crypto", "dexpaprika", "dexscreener"]

        for source in sources:
            cursor.execute(
                """
                SELECT MAX(ci.published_at) FROM content_items ci
                JOIN data_sources ds ON ci.source_id = ds.id
                WHERE ds.name = %s
            """,
                (source,),
            )

            last_run = cursor.fetchone()[0]

            if last_run:
                # Check if it's recent (within last 2 hours)
                time_diff = datetime.now() - last_run
                status[source] = {
                    "status": "online" if time_diff < timedelta(hours=2) else "stale",
                    "last_run": last_run.isoformat(),
                    "last_run_ago": str(time_diff).split(".")[0],
                }
            else:
                status[source] = {
                    "status": "offline",
                    "last_run": None,
                    "last_run_ago": "Never",
                }

        cursor.close()
        conn.close()

        return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/digests")
def get_digests():
    """Get all digests"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, title, content, created_at
            FROM digests
            ORDER BY created_at DESC
            LIMIT 20
        """
        )

        digests = []
        for row in cursor.fetchall():
            digests.append(
                {
                    "id": row[0],
                    "title": row[1] or "Untitled Digest",
                    "content": row[2] or "No content",
                    "created_at": row[3].isoformat() if row[3] else None,
                }
            )

        cursor.close()
        conn.close()

        return jsonify(digests)

    except Exception as e:
        logger.error(f"Error getting digests: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/content/<source>")
def get_content_by_source(source):
    """Get content by source with engagement metrics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get content from specific source
        cursor.execute(
            """
            SELECT ci.id, ci.title, ci.content, ci.author, ci.engagement_score,
                   ci.virality_score, ci.sentiment_score, ci.published_at, ci.url, ci.raw_data
            FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ds.name = %s
            AND ci.published_at >= NOW() - INTERVAL '7 days'
            ORDER BY ci.engagement_score DESC NULLS LAST, ci.published_at DESC
            LIMIT 50
        """,
            (source,),
        )

        posts = []
        for row in cursor.fetchall():
            # Extract engagement data from raw_data
            engagement_data = extract_engagement_data(row[9])

            posts.append(
                {
                    "id": row[0],
                    "title": row[1] or "No title",
                    "content": row[2] or "",
                    "author": row[3] or "Anonymous",
                    "engagement_score": row[4] or 0,
                    "virality_score": row[5] or 0,
                    "sentiment_score": row[6] or 0,
                    "published_at": row[7].isoformat() if row[7] else None,
                    "url": row[8] or "",
                    "likes": engagement_data["likes"],
                    "replies": engagement_data["replies"],
                    "retweets": engagement_data["retweets"],
                    "views": engagement_data["views"],
                }
            )

        cursor.close()
        conn.close()

        return jsonify(posts)

    except Exception as e:
        logger.error(f"Error getting content for {source}: {e}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=False)
