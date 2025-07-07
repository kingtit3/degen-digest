#!/usr/bin/env python3
"""
FarmChecker.xyz API Server
Connects to Cloud SQL and serves data to the frontend
"""

import json
import logging
import os
import traceback
import time
import uuid
from datetime import datetime, timedelta

import psycopg2
from flask import Flask, jsonify, request, send_from_directory, g
from flask_cors import CORS

# Import enhanced logging
from enhanced_logging_config import (
    get_logger, performance_monitor, log_request_context, 
    LogContext, request_id, user_agent, client_ip
)

# Initialize enhanced logger
logger = get_logger("web")
enhanced_logger = get_logger("web")

# Configure basic logging for compatibility
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Only use console logging for Cloud Run
    ],
)

app = Flask(__name__)
CORS(app)

# Flask middleware for request/response logging
@app.before_request
def before_request():
    """Log incoming requests"""
    g.start_time = time.time()
    g.request_id = str(uuid.uuid4())
    request_id.set(g.request_id)
    
    # Log request context
    log_request_context(request)
    
    enhanced_logger.logger.info(
        f"Incoming request: {request.method} {request.path}",
        extra={
            "context": LogContext(
                request_id=g.request_id,
                operation="request_start",
                component="api",
                metadata={
                    "method": request.method,
                    "path": request.path,
                    "query_params": dict(request.args),
                    "user_agent": request.headers.get('User-Agent', ''),
                    "client_ip": request.headers.get('X-Forwarded-For', request.remote_addr),
                    "content_length": request.content_length or 0
                }
            )
        }
    )

@app.after_request
def after_request(response):
    """Log outgoing responses"""
    if hasattr(g, 'start_time'):
        duration_ms = (time.time() - g.start_time) * 1000
        
        enhanced_logger.log_api_request(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            request_size=request.content_length or 0,
            response_size=len(response.get_data()) if response.get_data() else 0
        )
        
        enhanced_logger.logger.info(
            f"Request completed: {request.method} {request.path} - {response.status_code} ({duration_ms:.2f}ms)",
            extra={
                "context": LogContext(
                    request_id=g.request_id,
                    operation="request_complete",
                    component="api",
                    duration_ms=duration_ms,
                    success=200 <= response.status_code < 400,
                    metadata={
                        "status_code": response.status_code,
                        "response_size": len(response.get_data()) if response.get_data() else 0
                    }
                )
            }
        )
    
    return response

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "34.9.71.174"),
    "database": os.getenv("DB_NAME", "degen_digest"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "DegenDigest2024!"),
    "port": os.getenv("DB_PORT", "5432"),
}


@performance_monitor("database_connection")
def get_db_connection():
    """Create database connection with comprehensive logging"""
    start_time = time.time()
    
    try:
        enhanced_logger.logger.info(
            "Attempting database connection",
            extra={
                "context": LogContext(
                    request_id=request_id.get(),
                    operation="database_connection",
                    component="database",
                    metadata={
                        "host": DB_CONFIG["host"],
                        "database": DB_CONFIG["database"],
                        "port": DB_CONFIG["port"]
                    }
                )
            }
        )
        
        conn = psycopg2.connect(**DB_CONFIG)
        
        duration_ms = (time.time() - start_time) * 1000
        enhanced_logger.log_database_operation(
            operation="connect",
            table="connection",
            duration_ms=duration_ms,
            success=True
        )
        
        enhanced_logger.logger.info(
            f"Database connection successful ({duration_ms:.2f}ms)",
            extra={
                "context": LogContext(
                    request_id=request_id.get(),
                    operation="database_connection",
                    component="database",
                    duration_ms=duration_ms,
                    success=True
                )
            }
        )
        
        return conn
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        enhanced_logger.log_error(
            error=e,
            operation="database_connection",
            component="database",
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            port=DB_CONFIG["port"]
        )
        
        enhanced_logger.log_database_operation(
            operation="connect",
            table="connection",
            duration_ms=duration_ms,
            success=False,
            error=str(e)
        )
        
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
    """Extract crypto market data from raw_data JSON with comprehensive logging"""
    logger.debug(f"Starting crypto data extraction | type={type(raw_data).__name__} | length={len(str(raw_data)) if raw_data else 0}")
    try:
        if not raw_data:
            logger.debug("Raw data is empty, returning empty dict")
            return {}

        # Parse JSON if needed
        if isinstance(raw_data, str):
            logger.debug("Parsing JSON string")
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                logger.debug("String is not valid JSON, treating as plain text")
                # If it's not JSON, it might be plain text (like DexScreener descriptions)
                # Return a basic structure for plain text
                return {
                    "price": 0,
                    "price_change_24h": 0,
                    "price_change_percentage_24h": 0,
                    "market_cap": 0,
                    "volume_24h": 0,
                    "symbol": raw_data.split()[0].upper() if raw_data else "",
                    "name": raw_data,
                    "image": "",
                    "rank": 0,
                }
        else:
            data = raw_data

        logger.debug(f"Parsed data structure | keys={list(data.keys()) if isinstance(data, dict) else 'not_dict'} | type={type(data).__name__}")

        # Handle different crypto data structures based on actual database data
        if "current_price" in data and "symbol" in data:
            logger.debug("Processing CoinGecko format data")
            result = {
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
            logger.info(f"Extracted CoinGecko data | symbol={result['symbol']} | name={result['name']} | price={result['price']} | format=coingecko")
            return result
            
        elif "price_usd" in data:
            logger.debug("Processing DexPaprika format data")
            result = {
                "price": float(data.get("price_usd", 0)),
                "price_change_24h": float(data.get("24h", {}).get("last_price_usd_change", 0)),
                "price_change_percentage_24h": float(data.get("24h", {}).get("last_price_usd_change", 0)),
                "market_cap": float(data.get("fdv", 0)),
                "volume_24h": float(data.get("24h", {}).get("volume_usd", 0)),
                "symbol": data.get("symbol", "").upper(),
                "name": data.get("name", ""),
                "image": data.get("icon", ""),
                "rank": 0,
            }
            logger.info(f"Extracted DexPaprika data | symbol={result['symbol']} | name={result['name']} | price={result['price']} | format=dexpaprika")
            return result
            
        elif "tokenAddress" in data and "chainId" in data:
            logger.debug("Processing DexScreener format data")
            # Extract symbol from tokenAddress or description
            symbol = ""
            name = ""
            if "description" in data:
                name = data.get("description", "")
                # Try to extract symbol from description
                if "(" in name and ")" in name:
                    symbol = name.split("(")[-1].split(")")[0].replace("$", "")
                else:
                    symbol = name.split()[0] if name else ""
            
            result = {
                "price": 0,  # DexScreener data doesn't have direct price
                "price_change_24h": 0,
                "price_change_percentage_24h": 0,
                "market_cap": 0,
                "volume_24h": 0,
                "symbol": symbol.upper(),
                "name": name,
                "image": data.get("icon", ""),
                "rank": 0,
            }
            logger.info(f"Extracted DexScreener data | symbol={result['symbol']} | name={result['name']} | description={name} | format=dexscreener")
            return result
            
        elif "price" in data and "symbol" in data:
            logger.debug("Processing generic format data")
            result = {
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
            logger.info(f"Extracted generic format data | symbol={result['symbol']} | name={result['name']} | price={result['price']} | format=generic")
            return result
        else:
            logger.debug("Processing fallback format data")
            result = {
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
            logger.info(f"Extracted fallback format data | symbol={result['symbol']} | name={result['name']} | price={result['price']} | format=fallback")
            return result

    except Exception as e:
        logger.error(f"Error extracting crypto data: {e}\n{traceback.format_exc()} | raw_data_sample={str(raw_data)[:200] if raw_data else 'None'}")
        return {}


@performance_monitor("content_cleaning")
def clean_post_content(content):
    """Clean post content by extracting actual tweet text from raw data with comprehensive logging"""
    import re
    
    start_time = time.time()
    content_id = str(uuid.uuid4())[:8]
    input_length = len(str(content)) if content else 0
    
    enhanced_logger.logger.debug(
        f"Starting content cleaning for content_id={content_id}",
        extra={
            "context": LogContext(
                request_id=request_id.get(),
                operation="content_cleaning_start",
                component="content",
                metadata={
                    "content_id": content_id,
                    "input_length": input_length,
                    "content_type": type(content).__name__,
                    "content_preview": str(content)[:100] if content else ""
                }
            )
        }
    )
    
    if not content:
        enhanced_logger.log_content_processing(
            content_type="post",
            content_id=content_id,
            operation="clean",
            input_length=0,
            output_length=0,
            duration_ms=(time.time() - start_time) * 1000,
            success=True,
            cleaning_method="empty_content"
        )
        return ""

    # If content is JSON string, try to extract readable text
    if content.startswith("{") and content.endswith("}"):
        enhanced_logger.logger.debug(f"Processing JSON content for {content_id}")
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
                result = " ".join(readable_fields)
                duration_ms = (time.time() - start_time) * 1000
                enhanced_logger.log_content_processing(
                    content_type="post",
                    content_id=content_id,
                    operation="clean",
                    input_length=input_length,
                    output_length=len(result),
                    duration_ms=duration_ms,
                    success=True,
                    cleaning_method="json_extraction",
                    fields_found=list(data.keys()) if isinstance(data, dict) else []
                )
                return result
        except Exception as e:
            enhanced_logger.logger.debug(f"JSON parsing failed for {content_id}: {str(e)}")

    # Try to extract text from Python dict-like strings
    if "'text':" in content:
        enhanced_logger.logger.debug(f"Processing Python dict content for {content_id}")
        try:
            text_match = re.search(r"'text':\s*'([^']+)'", content)
            if text_match:
                text = text_match.group(1)
                # Clean up escaped characters
                text = text.replace('\\n', ' ').replace('\\t', ' ')
                text = text.replace('\\"', '"').replace("\\'", "'")
                text = text.replace('\u2014', '-')  # Handle em dash
                if len(text) > 10:  # Only return if it's substantial text
                    duration_ms = (time.time() - start_time) * 1000
                    enhanced_logger.log_content_processing(
                        content_type="post",
                        content_id=content_id,
                        operation="clean",
                        input_length=input_length,
                        output_length=len(text),
                        duration_ms=duration_ms,
                        success=True,
                        cleaning_method="python_dict_extraction",
                        pattern_matched="'text':"
                    )
                    return text
        except Exception as e:
            enhanced_logger.logger.debug(f"Python dict extraction failed for {content_id}: {str(e)}")

    # If content looks like raw JSON data, try to extract the actual tweet text
    if "text" in content and ("source" in content or "username" in content):
        enhanced_logger.logger.debug(f"Processing raw JSON-like content for {content_id}")
        try:
            # Look for text field in JSON-like content
            text_patterns = [
                r'"text":\s*"([^"]+)"',
                r"'text':\s*'([^']+)'",
                r'"content":\s*"([^"]+)"',
                r"'content':\s*'([^']+)'",
            ]
            
            for pattern in text_patterns:
                match = re.search(pattern, content)
                if match:
                    text = match.group(1)
                    # Clean up escaped characters
                    text = text.replace('\\n', ' ').replace('\\t', ' ')
                    text = text.replace('\\"', '"').replace("\\'", "'")
                    if len(text) > 10:  # Only return if it's substantial text
                        duration_ms = (time.time() - start_time) * 1000
                        enhanced_logger.log_content_processing(
                            content_type="post",
                            content_id=content_id,
                            operation="clean",
                            input_length=input_length,
                            output_length=len(text),
                            duration_ms=duration_ms,
                            success=True,
                            cleaning_method="regex_pattern_extraction",
                            pattern_used=pattern
                        )
                        return text
        except Exception as e:
            enhanced_logger.log_error(
                error=e,
                operation="content_cleaning",
                component="content",
                content_id=content_id,
                cleaning_method="regex_pattern_extraction"
            )

    # If it's plain text (not JSON), return as is
    if not content.startswith("{") and not content.startswith("["):
        enhanced_logger.logger.debug(f"Processing plain text content for {content_id}")
        # Clean up basic formatting
        content = content.replace('\\n', ' ').replace('\\t', ' ')
        content = content.replace('\\"', '"').replace("\\'", "'")
        content = re.sub(r'\s+', ' ', content).strip()
        
        if len(content) > 5:
            duration_ms = (time.time() - start_time) * 1000
            enhanced_logger.log_content_processing(
                content_type="post",
                content_id=content_id,
                operation="clean",
                input_length=input_length,
                output_length=len(content),
                duration_ms=duration_ms,
                success=True,
                cleaning_method="plain_text_cleaning"
            )
            return content

    # If we can't extract meaningful content, return empty
    duration_ms = (time.time() - start_time) * 1000
    enhanced_logger.log_content_processing(
        content_type="post",
        content_id=content_id,
        operation="clean",
        input_length=input_length,
        output_length=0,
        duration_ms=duration_ms,
        success=True,
        cleaning_method="no_extraction_possible"
    )
    
    enhanced_logger.logger.warning(
        f"Could not extract meaningful content for {content_id}",
        extra={
            "context": LogContext(
                request_id=request_id.get(),
                operation="content_cleaning_failed",
                component="content",
                duration_ms=duration_ms,
                success=False,
                metadata={
                    "content_id": content_id,
                    "input_length": input_length,
                    "content_preview": str(content)[:200] if content else ""
                }
            )
        }
    )
    
    return ""


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

    # If title is too short or technical, return empty instead of generic fallback
    if len(title) < 3 or title.startswith("{"):
        return ""

    return title


def extract_news_metadata(raw_data):
    """Extract published date and source from news raw_data"""
    try:
        if not raw_data:
            return None, None
            
        data = raw_data if isinstance(raw_data, dict) else json.loads(raw_data)
        
        # Extract published date
        published = None
        if "published" in data:
            published = data["published"]
        elif "publishedAt" in data:
            published = data["publishedAt"]
        elif "date" in data:
            published = data["date"]
            
        # Extract source
        source = None
        if "source" in data:
            source_data = data["source"]
            if isinstance(source_data, dict):
                source = source_data.get("name") or source_data.get("title")
            else:
                source = str(source_data)
        elif "author" in data:
            source = data["author"]
            
        return published, source
        
    except Exception as e:
        logger.error(f"Error extracting news metadata: {e}")
        return None, None


@app.route("/")
def index():
    """Serve the main HTML file"""
    return send_from_directory(".", "index.html")


@app.route("/crypto")
def crypto():
    """Serve the crypto page"""
    return send_from_directory(".", "crypto.html")


@app.route("/dex")
def dex():
    """Serve the dex page"""
    return send_from_directory(".", "dex.html")


@app.route("/twitter")
def twitter():
    """Serve the twitter page"""
    return send_from_directory(".", "twitter.html")


@app.route("/reddit")
def reddit():
    """Serve the reddit page"""
    return send_from_directory(".", "reddit.html")

@app.route("/news")
def news():
    """Serve the news page"""
    return send_from_directory(".", "news.html")


@app.route("/analytics")
def analytics():
    """Serve the analytics page"""
    return send_from_directory(".", "analytics.html")


@app.route("/status")
def status():
    """Serve the status page"""
    return send_from_directory(".", "status.html")


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(".", filename)


@app.route("/api/stats")
def get_stats():
    """Get overall statistics from dedicated tables"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get counts for each source from dedicated tables
        stats = {}

        # Twitter posts count
        cursor.execute(
            """
            SELECT COUNT(*) FROM tweets
            WHERE collected_at >= NOW() - INTERVAL '24 hours'
        """
        )
        stats["twitter_posts"] = cursor.fetchone()[0]

        # Reddit posts count
        cursor.execute(
            """
            SELECT COUNT(*) FROM reddit_posts
            WHERE collected_at >= NOW() - INTERVAL '24 hours'
        """
        )
        stats["reddit_posts"] = cursor.fetchone()[0]

        # News articles count
        cursor.execute(
            """
            SELECT COUNT(*) FROM articles
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """
        )
        stats["news_articles"] = cursor.fetchone()[0]

        # Crypto tokens count
        cursor.execute(
            """
            SELECT COUNT(*) FROM crypto_tokens
            WHERE last_updated_at >= NOW() - INTERVAL '24 hours'
        """
        )
        stats["crypto_tokens"] = cursor.fetchone()[0]

        # DexScreener pairs count
        cursor.execute(
            """
            SELECT COUNT(*) FROM dexscreener_pairs
            WHERE collected_at >= NOW() - INTERVAL '24 hours'
        """
        )
        stats["dexscreener_pairs"] = cursor.fetchone()[0]

        # DexPaprika tokens count
        cursor.execute(
            """
            SELECT COUNT(*) FROM dexpaprika_pairs
            WHERE collected_at >= NOW() - INTERVAL '24 hours'
        """
        )
        stats["dexpaprika_tokens"] = cursor.fetchone()[0]

        # Total engagement from all sources
        cursor.execute(
            """
            SELECT 
                COALESCE(SUM(likes_count + retweets_count + replies_count), 0) as twitter_engagement,
                COALESCE(SUM(score + comments_count), 0) as reddit_engagement,
                COALESCE(SUM(engagement_score), 0) as news_engagement
            FROM (
                SELECT likes_count, retweets_count, replies_count, 0 as score, 0 as comments_count, 0 as engagement_score
                FROM tweets WHERE collected_at >= NOW() - INTERVAL '24 hours'
                UNION ALL
                SELECT 0, 0, 0, score, comments_count, 0
                FROM reddit_posts WHERE collected_at >= NOW() - INTERVAL '24 hours'
                UNION ALL
                SELECT 0, 0, 0, 0, 0, engagement_score
                FROM articles WHERE created_at >= NOW() - INTERVAL '24 hours'
            ) combined_engagement
        """
        )
        engagement_row = cursor.fetchone()
        stats["total_engagement"] = (engagement_row[0] or 0) + (engagement_row[1] or 0) + (engagement_row[2] or 0)

        cursor.close()
        conn.close()

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500


def format_token_display(token_data):
    """Format token data for display with proper fallbacks"""
    try:
        # Extract basic info
        symbol = token_data.get("symbol", "").upper()
        name = token_data.get("name", symbol)
        price_usd = token_data.get("price_usd", 0)
        price_change_24h = token_data.get("price_change_24h", 0)
        price_change_percentage_24h = token_data.get("price_change_percentage_24h", 0)
        market_cap = token_data.get("market_cap", 0)
        volume_24h = token_data.get("volume_24h", 0)
        network = token_data.get("network", "")
        contract_address = token_data.get("contract_address", "")
        last_updated_at = token_data.get("last_updated_at", "")

        # Format price with proper decimal places
        if price_usd and price_usd > 0:
            if price_usd >= 1:
                formatted_price = f"${price_usd:,.2f}"
            elif price_usd >= 0.01:
                formatted_price = f"${price_usd:.4f}"
            else:
                formatted_price = f"${price_usd:.8f}"
        else:
            formatted_price = "—"

        # Format market cap
        if market_cap and market_cap > 0:
            if market_cap >= 1e9:
                formatted_market_cap = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                formatted_market_cap = f"${market_cap/1e6:.2f}M"
            elif market_cap >= 1e3:
                formatted_market_cap = f"${market_cap/1e3:.2f}K"
            else:
                formatted_market_cap = f"${market_cap:.2f}"
        else:
            formatted_market_cap = "—"

        # Format volume
        if volume_24h and volume_24h > 0:
            if volume_24h >= 1e9:
                formatted_volume = f"${volume_24h/1e9:.2f}B"
            elif volume_24h >= 1e6:
                formatted_volume = f"${volume_24h/1e6:.2f}M"
            elif volume_24h >= 1e3:
                formatted_volume = f"${volume_24h/1e3:.2f}K"
            else:
                formatted_volume = f"${volume_24h:.2f}"
        else:
            formatted_volume = "—"

        # Format price change
        if price_change_percentage_24h != 0:
            formatted_change = f"{price_change_percentage_24h:+.2f}%"
        else:
            formatted_change = "0.00%"

        return {
            "id": token_data.get("id", 0),
            "symbol": symbol,
            "name": name,
            "price": formatted_price,
            "price_change_24h": formatted_change,
            "price_change_percentage_24h": price_change_percentage_24h,
            "market_cap": formatted_market_cap,
            "volume_24h": formatted_volume,
            "rank": 0,  # Not available in current schema
            "image": "",  # Not available in current schema
            "source": network or "unknown",
            "updated_at": last_updated_at or datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error formatting token display: {e}")
        return {
            "id": 0,
            "symbol": "UNKNOWN",
            "name": "Unknown Token",
            "price": "—",
            "price_change_24h": "0.00%",
            "price_change_percentage_24h": 0,
            "market_cap": "—",
            "volume_24h": "—",
            "rank": 0,
            "image": "",
            "source": "unknown",
            "updated_at": datetime.now().isoformat(),
        }


@app.route("/api/crypto/top-gainers")
def get_top_gainers():
    """Get top gaining crypto tokens from dedicated crypto_tokens table"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get top gainers from crypto_tokens table, prioritizing most recent data for each symbol
        cursor.execute("""
            SELECT DISTINCT ON (symbol) id, symbol, name, price_usd, price_change_24h, market_cap, volume_24h, 
                   network, contract_address, last_updated_at
            FROM crypto_tokens 
            WHERE price_change_24h > 0 
            AND price_usd > 0
            AND last_updated_at >= NOW() - INTERVAL '24 hours'
            ORDER BY symbol, last_updated_at DESC, price_change_24h DESC
            LIMIT 20
        """)

        gainers = []
        for row in cursor.fetchall():
            symbol = row[1] or ""
            name = row[2] or symbol
            
            # Clean up name and symbol
            if name and "(" in name and ")" in name:
                # Extract symbol from parentheses if present
                symbol = name.split("(")[-1].split(")")[0].replace("$", "")
                name = name.split("(")[0].strip()
            
            token_data = {
                'id': row[0],
                'symbol': symbol.upper(),
                'name': name,
                'price_usd': float(row[3]) if row[3] else 0,
                'price_change_24h': float(row[4]) if row[4] else 0,
                'price_change_percentage_24h': float(row[4]) if row[4] else 0,  # Assuming percentage
                'market_cap': float(row[5]) if row[5] else 0,
                'volume_24h': float(row[6]) if row[6] else 0,
                'network': row[7] or '',
                'contract_address': row[8] or '',
                'last_updated_at': row[9].isoformat() if row[9] else None,
            }
            gainers.append(format_token_display(token_data))

        cursor.close()
        conn.close()

        logger.info(f"Top gainers API response prepared | total_gainers={len(gainers)} | symbols={[g.get('symbol') for g in gainers]}")

        # If no real data, provide fallback data
        if not gainers:
            logger.warning("No gainers found in crypto_tokens table, returning empty list")
            gainers = []

        return jsonify(gainers[:10])

    except Exception as e:
        logger.error(f"Error getting top gainers: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/crypto/trending")
def get_trending_crypto():
    """Get trending crypto tokens from dedicated crypto_tokens table"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get trending tokens by volume and recent updates, prioritizing most recent data for each symbol
        cursor.execute("""
            SELECT DISTINCT ON (symbol) id, symbol, name, price_usd, price_change_24h, market_cap, volume_24h, 
                   network, contract_address, last_updated_at
            FROM crypto_tokens 
            WHERE volume_24h > 0 
            AND price_usd > 0
            AND last_updated_at >= NOW() - INTERVAL '24 hours'
            ORDER BY symbol, last_updated_at DESC, volume_24h DESC
            LIMIT 20
        """)

        trending = []
        for row in cursor.fetchall():
            symbol = row[1] or ""
            name = row[2] or symbol
            
            # Clean up name and symbol
            if name and "(" in name and ")" in name:
                # Extract symbol from parentheses if present
                symbol = name.split("(")[-1].split(")")[0].replace("$", "")
                name = name.split("(")[0].strip()
            
            token_data = {
                'id': row[0],
                'symbol': symbol.upper(),
                'name': name,
                'price_usd': float(row[3]) if row[3] else 0,
                'price_change_24h': float(row[4]) if row[4] else 0,
                'price_change_percentage_24h': float(row[4]) if row[4] else 0,  # Assuming percentage
                'market_cap': float(row[5]) if row[5] else 0,
                'volume_24h': float(row[6]) if row[6] else 0,
                'network': row[7] or '',
                'contract_address': row[8] or '',
                'last_updated_at': row[9].isoformat() if row[9] else None,
            }
            trending.append(format_token_display(token_data))

        cursor.close()
        conn.close()

        # If no real data, provide fallback data
        if not trending:
            logger.warning("No trending tokens found in crypto_tokens table, returning empty list")
            trending = []

        return jsonify(trending[:10])

    except Exception as e:
        logger.error(f"Error getting trending crypto: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/crypto/meme-coins")
def get_meme_coins():
    """Get meme coins and viral tokens"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get meme coins by looking for specific keywords in names and symbols
        cursor.execute("""
            SELECT id, symbol, name, price_usd, price_change_24h, market_cap, volume_24h, 
                   network, contract_address, last_updated_at
            FROM crypto_tokens 
            WHERE (
                LOWER(name) LIKE '%dog%' OR 
                LOWER(name) LIKE '%cat%' OR 
                LOWER(name) LIKE '%moon%' OR 
                LOWER(name) LIKE '%inu%' OR 
                LOWER(name) LIKE '%pepe%' OR 
                LOWER(name) LIKE '%shib%' OR 
                LOWER(name) LIKE '%floki%' OR 
                LOWER(name) LIKE '%wojak%' OR 
                LOWER(name) LIKE '%chad%' OR 
                LOWER(name) LIKE '%based%' OR
                LOWER(symbol) LIKE '%DOGE%' OR 
                LOWER(symbol) LIKE '%SHIB%' OR 
                LOWER(symbol) LIKE '%PEPE%' OR 
                LOWER(symbol) LIKE '%FLOKI%' OR 
                LOWER(symbol) LIKE '%WOJAK%' OR 
                LOWER(symbol) LIKE '%CHAD%' OR 
                LOWER(symbol) LIKE '%BASED%'
            )
            AND price_usd > 0
            AND last_updated_at >= NOW() - INTERVAL '24 hours'
            ORDER BY volume_24h DESC, price_change_24h DESC
            LIMIT 20
        """)

        meme_coins = []
        for row in cursor.fetchall():
            symbol = row[1] or ""
            name = row[2] or symbol
            
            # Clean up name and symbol
            if name and "(" in name and ")" in name:
                # Extract symbol from parentheses if present
                symbol = name.split("(")[-1].split(")")[0].replace("$", "")
                name = name.split("(")[0].strip()
            
            token_data = {
                'id': row[0],
                'symbol': symbol.upper(),
                'name': name,
                'price_usd': float(row[3]) if row[3] else 0,
                'price_change_24h': float(row[4]) if row[4] else 0,
                'price_change_percentage_24h': float(row[4]) if row[4] else 0,
                'market_cap': float(row[5]) if row[5] else 0,
                'volume_24h': float(row[6]) if row[6] else 0,
                'network': row[7] or '',
                'contract_address': row[8] or '',
                'last_updated_at': row[9].isoformat() if row[9] else None,
            }
            meme_coins.append(format_token_display(token_data))

        cursor.close()
        conn.close()

        # If no meme coins found, provide some popular ones
        if not meme_coins:
            logger.warning("No meme coins found, returning popular meme coins")
            meme_coins = [
                {
                    "id": 1,
                    "symbol": "DOGE",
                    "name": "Dogecoin",
                    "price": "$0.12",
                    "price_change_24h": "+5.2%",
                    "price_change_percentage_24h": 5.2,
                    "market_cap": "$17.2B",
                    "volume_24h": "$890M",
                    "source": "meme",
                    "updated_at": datetime.now().isoformat(),
                },
                {
                    "id": 2,
                    "symbol": "SHIB",
                    "name": "Shiba Inu",
                    "price": "$0.000023",
                    "price_change_24h": "+3.8%",
                    "price_change_percentage_24h": 3.8,
                    "market_cap": "$13.5B",
                    "volume_24h": "$450M",
                    "source": "meme",
                    "updated_at": datetime.now().isoformat(),
                },
                {
                    "id": 3,
                    "symbol": "PEPE",
                    "name": "Pepe",
                    "price": "$0.0000089",
                    "price_change_24h": "+12.4%",
                    "price_change_percentage_24h": 12.4,
                    "market_cap": "$3.7B",
                    "volume_24h": "$280M",
                    "source": "meme",
                    "updated_at": datetime.now().isoformat(),
                }
            ]

        return jsonify(meme_coins[:10])

    except Exception as e:
        logger.error(f"Error getting meme coins: {e}")
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


@app.route("/api/twitter")
@performance_monitor("twitter_api")
def get_twitter_posts():
    """Get tweets from the tweet table"""
    start_time = time.time()
    request_id_val = str(uuid.uuid4())
    request_id.set(request_id_val)
    
    # Log request context
    log_request_context(request)
    
    enhanced_logger.logger.info(
        f"Twitter API request started - {request_id_val}",
        extra={
            "context": LogContext(
                request_id=request_id_val,
                operation="twitter_api_start",
                component="api",
                metadata={
                    "method": request.method,
                    "path": request.path,
                    "query_params": dict(request.args),
                    "user_agent": request.headers.get('User-Agent', ''),
                    "client_ip": request.headers.get('X-Forwarded-For', request.remote_addr)
                }
            )
        }
    )
    
    try:
        # Database connection
        db_start_time = time.time()
        conn = get_db_connection()
        db_connect_time = (time.time() - db_start_time) * 1000
        
        if not conn:
            enhanced_logger.log_error(
                Exception("Database connection failed"),
                operation="twitter_api",
                component="database",
                request_id=request_id_val
            )
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get sort parameter from query string
        sort_by = request.args.get('sort', 'recent')
        enhanced_logger.logger.debug(f"Sort parameter: {sort_by}")
        
        if sort_by == 'engagement':
            order_clause = "ORDER BY (like_count + retweet_count + reply_count) DESC"
        elif sort_by == 'likes':
            order_clause = "ORDER BY like_count DESC"
        elif sort_by == 'retweets':
            order_clause = "ORDER BY retweet_count DESC"
        else:
            order_clause = "ORDER BY created_at DESC"

        # Execute query
        query_start_time = time.time()
        cursor.execute(
            f"""
            SELECT id, tweet_id, content, author_username, author_followers_count,
                   author_verified, likes_count, retweets_count, replies_count, views_count,
                   0 as quote_count, 0 as bookmark_count, published_at, collected_at
            FROM tweets
            WHERE published_at >= NOW() - INTERVAL '7 days'
            {order_clause}
            LIMIT 50
        """
        )
        query_time = (time.time() - query_start_time) * 1000
        
        enhanced_logger.log_database_operation(
            operation="select",
            table="tweet",
            duration_ms=query_time,
            record_count=0,  # Will be updated after fetch
            success=True,
            query_type="twitter_posts",
            sort_by=sort_by
        )

        # Process results
        processing_start_time = time.time()
        rows = cursor.fetchall()
        fetch_time = (time.time() - processing_start_time) * 1000
        
        enhanced_logger.logger.info(
            f"Fetched {len(rows)} tweets in {fetch_time:.2f}ms",
            extra={
                "context": LogContext(
                    request_id=request_id_val,
                    operation="twitter_posts_fetch",
                    component="database",
                    duration_ms=fetch_time,
                    success=True,
                    metadata={
                        "rows_fetched": len(rows),
                        "query_time_ms": query_time
                    }
                )
            }
        )

        posts = []
        content_processing_stats = {
            "total_processed": 0,
            "successful_cleaning": 0,
            "failed_cleaning": 0
        }
        
        for i, row in enumerate(rows):
            content_processing_stats["total_processed"] += 1
            
            # Clean the tweet text
            clean_content = clean_post_content(row[2])
            
            if clean_content:
                content_processing_stats["successful_cleaning"] += 1
                
                # Create tweet URL
                tweet_url = f"https://twitter.com/{row[3]}/status/{row[1]}"
                
                posts.append(
                    {
                        "id": row[0],
                        "tweet_id": row[1],
                        "title": f"Tweet by @{row[3]}",
                        "content": clean_content,
                        "author": f"@{row[3]}",
                        "user_screen_name": row[3],
                        "user_followers_count": row[4],
                        "user_verified": row[5],
                        "engagement_score": row[6] + row[7] + row[8],  # likes + retweets + replies
                        "virality_score": row[6] + row[7] * 2,  # likes + retweets*2
                        "sentiment_score": 0,  # Could be calculated later
                        "published_at": row[12].isoformat() if row[12] else None,
                        "scraped_at": row[13].isoformat() if row[13] else None,
                        "url": tweet_url,
                        "likes": row[6],
                        "replies": row[8],
                        "retweets": row[7],
                        "views": row[9] or 0,
                        "quote_count": row[10] or 0,
                        "bookmark_count": row[11] or 0,
                    }
                )
            else:
                content_processing_stats["failed_cleaning"] += 1

        processing_time = (time.time() - processing_start_time) * 1000
        
        enhanced_logger.log_content_processing(
            content_type="twitter_posts",
            content_id=f"batch_{request_id_val}",
            operation="batch_processing",
            input_length=len(rows),
            output_length=len(posts),
            duration_ms=processing_time,
            success=True,
            **content_processing_stats
        )

        cursor.close()
        conn.close()

        # Calculate total response time
        total_time = (time.time() - start_time) * 1000
        
        # Log business metrics
        enhanced_logger.log_business_metric(
            metric_name="twitter_posts_retrieved",
            value=len(posts),
            category="content_retrieval",
            total_time_ms=total_time,
            db_connect_time_ms=db_connect_time,
            query_time_ms=query_time,
            processing_time_ms=processing_time
        )
        
        # Log API request completion
        enhanced_logger.log_api_request(
            method=request.method,
            path=request.path,
            status_code=200,
            duration_ms=total_time,
            response_size=len(str(posts)),
            posts_count=len(posts),
            **content_processing_stats
        )

        enhanced_logger.logger.info(
            f"Twitter posts API completed - {len(posts)} posts in {total_time:.2f}ms",
            extra={
                "context": LogContext(
                    request_id=request_id_val,
                    operation="twitter_posts_api_complete",
                    component="api",
                    duration_ms=total_time,
                    success=True,
                    metadata={
                        "posts_returned": len(posts),
                        "db_connect_time_ms": db_connect_time,
                        "query_time_ms": query_time,
                        "processing_time_ms": processing_time,
                        **content_processing_stats
                    }
                )
            }
        )
        
        return jsonify(posts)

    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        
        enhanced_logger.log_error(
            error=e,
            operation="twitter_posts_api",
            component="api",
            request_id=request_id_val,
            duration_ms=total_time
        )
        
        enhanced_logger.log_api_request(
            method=request.method,
            path=request.path,
            status_code=500,
            duration_ms=total_time,
            error=str(e)
        )
        
        return jsonify({"error": str(e)}), 500


@app.route("/api/reddit")
def get_reddit_posts():
    """Get Reddit posts from the redditpost table"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get sort parameter from query string
        sort_by = request.args.get('sort', 'recent')
        
        if sort_by == 'score':
            order_clause = "ORDER BY score DESC"
        elif sort_by == 'comments':
            order_clause = "ORDER BY num_comments DESC"
        else:
            order_clause = "ORDER BY created_at DESC"

        # Get Reddit posts from the reddit_posts table
        cursor.execute(
            f"""
            SELECT id, post_id, title, author_username, subreddit, score, comments_count, 
                   published_at, url, collected_at
            FROM reddit_posts
            WHERE published_at >= NOW() - INTERVAL '7 days'
            {order_clause}
            LIMIT 50
        """
        )

        posts = []
        for row in cursor.fetchall():
            # Clean the title
            clean_title = clean_post_title(row[2])
            
            if clean_title:
                posts.append(
                    {
                        "id": row[0],
                        "post_id": row[1],
                        "title": clean_title,
                        "content": f"Reddit post from r/{row[4]}",
                        "author": row[3] or "Anonymous",
                        "subreddit": row[4],
                        "engagement_score": row[5] + row[6],  # score + comments
                        "virality_score": row[5] + row[6] * 2,  # score + comments*2
                        "sentiment_score": 0,  # Could be calculated later
                        "published_at": row[7].isoformat() if row[7] else None,
                        "scraped_at": row[9].isoformat() if row[9] else None,
                        "url": row[8],
                        "score": row[5],
                        "num_comments": row[6],
                        "upvotes": row[5],  # Reddit uses upvotes
                        "comments": row[6],
                    }
                )

        cursor.close()
        conn.close()

        # Return the posts found
        logger.info(f"Found {len(posts)} Reddit posts")
        return jsonify(posts)

    except Exception as e:
        logger.error(f"Error getting Reddit posts: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/news-posts")
def get_news_posts():
    """Get top news posts with engagement metrics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get sort parameter from query string
        sort_by = request.args.get('sort', 'engagement')
        
        if sort_by == 'published_at':
            order_clause = "ORDER BY ci.published_at DESC NULLS LAST"
        elif sort_by == 'recent':
            order_clause = "ORDER BY ci.created_at DESC NULLS LAST"
        else:
            order_clause = "ORDER BY ci.engagement_score DESC NULLS LAST, ci.published_at DESC"

        # Get top news posts with sorting
        cursor.execute(
            f"""
            SELECT id, title, content, author, engagement_score,
                   virality_score, sentiment_score, published_at, url, raw_data
            FROM articles
            WHERE created_at >= NOW() - INTERVAL '30 days'
            {order_clause}
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

            # Use original content if cleaned content is empty
            if not clean_content and row[2]:
                clean_content = row[2][:200] + "..." if len(row[2]) > 200 else row[2]
            
            # Use original title if cleaned title is empty
            if not clean_title and row[1]:
                clean_title = row[1]
            
            # Extract published date and source from raw_data if database fields are empty
            published_at = row[7]
            author = row[3]
            
            if not published_at or not author:
                extracted_published, extracted_source = extract_news_metadata(row[9])
                if not published_at and extracted_published:
                    try:
                        # Try to parse the date string
                        if isinstance(extracted_published, str):
                            # Handle different date formats
                            for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"]:
                                try:
                                    published_at = datetime.strptime(extracted_published, fmt)
                                    break
                                except:
                                    continue
                        else:
                            published_at = extracted_published
                    except:
                        pass
                
                if not author and extracted_source:
                    author = extracted_source
            
            # Include posts with any content or title, be more permissive
            if clean_content or clean_title or row[2] or row[1]:
                posts.append(
                    {
                        "id": row[0],
                        "title": row[1] or "No title",
                        "content": clean_content or "Content available",
                        "author": author or "Anonymous",
                        "engagement_score": row[4] or 0,
                        "virality_score": row[5] or 0,
                        "sentiment_score": row[6] or 0,
                        "published_at": published_at.isoformat() if published_at else None,
                        "url": row[8] or "",
                        "upvotes": engagement_data.get("likes", 0),
                        "comments": engagement_data.get("replies", 0),
                        "score": engagement_data.get("score", 0),
                        "raw_data": row[9],
                    }
                )

        cursor.close()
        conn.close()

        # Return the posts found (no fallback needed since there's plenty of data)
        logger.info(f"Found {len(posts)} news posts")
        return jsonify(posts)

    except Exception as e:
        logger.error(f"Error getting news posts: {e}")
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
    """Get comprehensive system status for all crawlers and migrations using dedicated status table"""
    try:
        # Get crawler status from the dedicated table
        status = get_crawler_status_from_db()
        
        # Add database and web application status
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Check database health
            cursor.execute("SELECT NOW() as db_time")
            db_time = cursor.fetchone()[0]
            status["database"] = {
                "status": "online",
                "last_check": db_time.isoformat(),
                "last_check_ago": "Just now",
                "connection": "healthy"
            }
            
            cursor.close()
            conn.close()
        else:
            status["database"] = {
                "status": "offline",
                "last_check": None,
                "last_check_ago": "Never",
                "connection": "failed"
            }

        # Check web application status
        status["web_application"] = {
            "status": "online",
            "last_check": datetime.now().isoformat(),
            "last_check_ago": "Just now",
            "version": "1.0.0"
        }

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


def update_crawler_status_db(crawler_name, status, items_collected=0, error_message=None):
    """Update crawler status in the database"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Database connection failed for crawler status update")
            return False

        cursor = conn.cursor()
        
        # Call the database function to update status
        cursor.execute(
            "SELECT update_crawler_status(%s, %s, %s, %s)",
            (crawler_name, status, items_collected, error_message)
        )
        
        # Update the hourly/daily counts
        cursor.execute("SELECT update_crawler_counts()")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Updated crawler status: {crawler_name} = {status}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating crawler status for {crawler_name}: {e}")
        return False


def get_crawler_status_from_db():
    """Get crawler status from the dedicated table"""
    try:
        conn = get_db_connection()
        if not conn:
            return {}

        cursor = conn.cursor()
        
        # Get status from the crawler_status table
        cursor.execute("""
            SELECT 
                crawler_name,
                status,
                last_run_at,
                last_successful_run_at,
                items_collected,
                items_collected_24h,
                items_collected_1h,
                error_message,
                updated_at
            FROM crawler_status
            ORDER BY crawler_name
        """)
        
        status = {}
        for row in cursor.fetchall():
            crawler_name, db_status, last_run, last_successful, total_items, items_24h, items_1h, error_msg, updated_at = row
            
            # Calculate time differences
            time_diff = None
            if last_run:
                time_diff = datetime.now() - last_run
                
            # Determine status level based on last run time
            if not last_run:
                status_level = "offline"
            elif time_diff and time_diff < timedelta(hours=1):
                status_level = "online"
            elif time_diff and time_diff < timedelta(hours=6):
                status_level = "recent"
            elif time_diff and time_diff < timedelta(hours=24):
                status_level = "stale"
            else:
                status_level = "offline"
            
            status[crawler_name] = {
                "status": status_level,
                "last_run": last_run.isoformat() if last_run else None,
                "last_run_ago": str(time_diff).split(".")[0] if time_diff else "Never",
                "last_successful_run": last_successful.isoformat() if last_successful else None,
                "total_items": total_items or 0,
                "items_24h": items_24h or 0,
                "items_1h": items_1h or 0,
                "error_message": error_msg,
                "updated_at": updated_at.isoformat() if updated_at else None,
                "data_freshness": "fresh" if items_1h and items_1h > 0 else "stale" if items_24h and items_24h > 0 else "old"
            }
        
        cursor.close()
        conn.close()
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting crawler status from database: {e}")
        return {}


@app.route("/api/update-crawler-status", methods=["POST"])
def update_crawler_status_endpoint():
    """Update crawler status via API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        crawler_name = data.get("crawler_name")
        status = data.get("status")
        items_collected = data.get("items_collected", 0)
        error_message = data.get("error_message")
        
        if not crawler_name or not status:
            return jsonify({"error": "crawler_name and status are required"}), 400
            
        success = update_crawler_status_db(crawler_name, status, items_collected, error_message)
        
        if success:
            return jsonify({"message": f"Updated {crawler_name} status to {status}"})
        else:
            return jsonify({"error": "Failed to update crawler status"}), 500
            
    except Exception as e:
        logger.error(f"Error updating crawler status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/refresh-crawler-status")
def refresh_crawler_status():
    """Refresh crawler status by updating counts from actual data"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()
        
        # Update the hourly/daily counts for all crawlers
        cursor.execute("SELECT update_crawler_counts()")
        
        # Get updated status
        status = get_crawler_status_from_db()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Crawler status refreshed successfully",
            "status": status
        })
        
    except Exception as e:
        logger.error(f"Error refreshing crawler status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/dex/dexscreener")
def get_dexscreener_pairs():
    """Get DexScreener pairs from dedicated dexscreener_pairs table"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get sort parameter from query string
        sort_by = request.args.get('sort', 'volume')
        
        if sort_by == 'price_change':
            order_clause = "ORDER BY price_change_24h DESC"
        elif sort_by == 'liquidity':
            order_clause = "ORDER BY liquidity_usd DESC"
        elif sort_by == 'recent':
            order_clause = "ORDER BY collected_at DESC"
        else:
            order_clause = "ORDER BY volume_24h DESC"

        # Get DexScreener pairs from the dexscreener_pairs table
        cursor.execute(
            f"""
            SELECT id, pair_id, base_token_symbol, base_token_name, base_token_address,
                   quote_token_symbol, quote_token_name, quote_token_address,
                   dex_id, chain_id, price_usd, price_change_24h, volume_24h, 
                   liquidity_usd, fdv, txns_24h, buys_24h, sells_24h, collected_at
            FROM dexscreener_pairs
            WHERE collected_at >= NOW() - INTERVAL '24 hours'
            AND price_usd > 0
            {order_clause}
            LIMIT 50
        """
        )

        pairs = []
        for row in cursor.fetchall():
            pairs.append({
                "id": row[0],
                "pair_id": row[1],
                "base_token_symbol": row[2] or "N/A",
                "base_token_name": row[3] or "Unknown",
                "base_token_address": row[4] or "",
                "quote_token_symbol": row[5] or "N/A",
                "quote_token_name": row[6] or "Unknown",
                "quote_token_address": row[7] or "",
                "dex": row[8] or "Unknown",
                "chain": row[9] or "Unknown",
                "price_usd": float(row[10]) if row[10] else 0,
                "price_change_24h": float(row[11]) if row[11] else 0,
                "volume_24h": float(row[12]) if row[12] else 0,
                "liquidity_usd": float(row[13]) if row[13] else 0,
                "fdv": float(row[14]) if row[14] else 0,
                "txns_24h": int(row[15]) if row[15] else 0,
                "buys_24h": int(row[16]) if row[16] else 0,
                "sells_24h": int(row[17]) if row[17] else 0,
                "collected_at": row[18].isoformat() if row[18] else None,
                "pair_name": f"{row[2] or 'N/A'}/{row[5] or 'N/A'}",
                "dex_url": f"https://dexscreener.com/{row[9] or 'unknown'}/{row[1]}"
            })

        cursor.close()
        conn.close()

        logger.info(f"Found {len(pairs)} DexScreener pairs")
        return jsonify(pairs)

    except Exception as e:
        logger.error(f"Error getting DexScreener pairs: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/dex/dexpaprika")
def get_dexpaprika_tokens():
    """Get DexPaprika tokens from dedicated dexpaprika_pairs table"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get sort parameter from query string
        sort_by = request.args.get('sort', 'volume')
        
        if sort_by == 'price_change':
            order_clause = "ORDER BY price_change_24h DESC"
        elif sort_by == 'liquidity':
            order_clause = "ORDER BY liquidity_usd DESC"
        elif sort_by == 'recent':
            order_clause = "ORDER BY collected_at DESC"
        else:
            order_clause = "ORDER BY volume_24h DESC"

        # Get DexPaprika tokens from the dexpaprika_pairs table
        cursor.execute(
            f"""
            SELECT id, pair_id, base_token_symbol, base_token_name, base_token_address,
                   dex_id, chain_id, price_usd, price_change_24h, volume_24h, 
                   liquidity_usd, txns_24h, market_cap, collected_at
            FROM dexpaprika_pairs
            WHERE collected_at >= NOW() - INTERVAL '24 hours'
            AND price_usd > 0
            {order_clause}
            LIMIT 50
        """
        )

        tokens = []
        for row in cursor.fetchall():
            tokens.append({
                "id": row[0],
                "token_id": row[1],
                "symbol": row[2] or "N/A",
                "name": row[3] or "Unknown",
                "address": row[4] or "",
                "dex": row[5] or "DexPaprika",
                "chain": row[6] or "Unknown",
                "price_usd": float(row[7]) if row[7] else 0,
                "price_change_24h": float(row[8]) if row[8] else 0,
                "volume_24h": float(row[9]) if row[9] else 0,
                "liquidity_usd": float(row[10]) if row[10] else 0,
                "txns_24h": int(row[11]) if row[11] else 0,
                "market_cap": float(row[12]) if row[12] else 0,
                "collected_at": row[13].isoformat() if row[13] else None,
                "token_url": f"https://dexpaprika.com/token/{row[4]}" if row[4] else ""
            })

        cursor.close()
        conn.close()

        logger.info(f"Found {len(tokens)} DexPaprika tokens")
        return jsonify(tokens)

    except Exception as e:
        logger.error(f"Error getting DexPaprika tokens: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/dex/combined")
def get_combined_dex_data():
    """Get combined DEX data from both DexScreener and DexPaprika"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        # Get sort parameter from query string
        sort_by = request.args.get('sort', 'volume')
        
        if sort_by == 'price_change':
            order_clause = "ORDER BY price_change_24h DESC"
        elif sort_by == 'liquidity':
            order_clause = "ORDER BY liquidity_usd DESC"
        elif sort_by == 'recent':
            order_clause = "ORDER BY collected_at DESC"
        else:
            order_clause = "ORDER BY volume_24h DESC"

        # Get combined data from both tables
        cursor.execute(
            f"""
            (SELECT 
                'dexscreener' as source,
                id, pair_id as token_id, base_token_symbol as symbol, base_token_name as name,
                base_token_address as address, dex_id as dex, chain_id as chain,
                price_usd, price_change_24h, volume_24h, liquidity_usd, fdv as market_cap,
                txns_24h, collected_at
            FROM dexscreener_pairs
            WHERE collected_at >= NOW() - INTERVAL '24 hours' AND price_usd > 0)
            UNION ALL
            (SELECT 
                'dexpaprika' as source,
                id, pair_id as token_id, base_token_symbol as symbol, base_token_name as name,
                base_token_address as address, dex_id as dex, chain_id as chain,
                price_usd, price_change_24h, volume_24h, liquidity_usd, market_cap,
                txns_24h, collected_at
            FROM dexpaprika_pairs
            WHERE collected_at >= NOW() - INTERVAL '24 hours' AND price_usd > 0)
            {order_clause}
            LIMIT 100
        """
        )

        combined_data = []
        for row in cursor.fetchall():
            combined_data.append({
                "source": row[0],
                "id": row[1],
                "token_id": row[2],
                "symbol": row[3] or "N/A",
                "name": row[4] or "Unknown",
                "address": row[5] or "",
                "dex": row[6] or "Unknown",
                "chain": row[7] or "Unknown",
                "price_usd": float(row[8]) if row[8] else 0,
                "price_change_24h": float(row[9]) if row[9] else 0,
                "volume_24h": float(row[10]) if row[10] else 0,
                "liquidity_usd": float(row[11]) if row[11] else 0,
                "market_cap": float(row[12]) if row[12] else 0,
                "txns_24h": int(row[13]) if row[13] else 0,
                "collected_at": row[14].isoformat() if row[14] else None
            })

        cursor.close()
        conn.close()

        logger.info(f"Found {len(combined_data)} combined DEX entries")
        return jsonify(combined_data)

    except Exception as e:
        logger.error(f"Error getting combined DEX data: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
