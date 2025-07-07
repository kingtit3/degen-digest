#!/usr/bin/env python3
"""
FarmChecker.xyz API Server - Simplified Version
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

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

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
        logger.error(f"Database connection failed: {e}")
        return None

@app.route("/")
def index():
    """Serve the main HTML file"""
    return send_from_directory(".", "index.html")

@app.route("/crypto")
def crypto():
    """Serve the crypto page"""
    return send_from_directory(".", "crypto.html")

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

@app.route("/api/twitter")
def get_twitter_posts():
    """Get Twitter posts from dedicated tweet table"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()
        
        # Get sort parameter
        sort_by = request.args.get('sort', 'recent')
        
        # Build query based on sort parameter
        if sort_by == 'recent':
            order_clause = "ORDER BY created_at DESC"
        elif sort_by == 'engagement':
            order_clause = "ORDER BY (like_count + reply_count * 2 + retweet_count * 3 + COALESCE(view_count, 0) * 0.1) DESC"
        elif sort_by == 'likes':
            order_clause = "ORDER BY like_count DESC"
        elif sort_by == 'retweets':
            order_clause = "ORDER BY retweet_count DESC"
        else:
            order_clause = "ORDER BY created_at DESC"
        
        # Get tweets from dedicated tweet table
        cursor.execute(f"""
            SELECT id, user_screen_name, user_verified, user_followers_count,
                   full_text, tweet_id, like_count, reply_count, retweet_count, 
                   view_count, quote_count, bookmark_count, created_at
            FROM tweet 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
            {order_clause}
            LIMIT 50
        """)
        
        tweets = []
        for row in cursor.fetchall():
            # Calculate engagement score
            engagement_score = (row[6] or 0) + (row[7] or 0) * 2 + (row[8] or 0) * 3 + (row[9] or 0) * 0.1
            
            tweets.append({
                "id": row[0],
                "user_screen_name": row[1],
                "user_verified": row[2],
                "user_followers_count": row[3],
                "content": row[4],
                "url": f"https://twitter.com/{row[1]}/status/{row[5]}" if row[1] and row[5] else None,
                "likes": row[6],
                "replies": row[7],
                "retweets": row[8],
                "views": row[9],
                "quote_count": row[10],
                "bookmark_count": row[11],
                "engagement_score": engagement_score,
                "published_at": row[12].isoformat() if row[12] else None
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(tweets)
        
    except Exception as e:
        logger.error(f"Error getting Twitter posts: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/reddit")
def get_reddit_posts():
    """Get Reddit posts from dedicated redditpost table"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()
        
        # Get sort parameter
        sort_by = request.args.get('sort', 'recent')
        
        # Build query based on sort parameter
        if sort_by == 'recent':
            order_clause = "ORDER BY created_at DESC"
        elif sort_by == 'score':
            order_clause = "ORDER BY score DESC"
        elif sort_by == 'comments':
            order_clause = "ORDER BY num_comments DESC"
        else:
            order_clause = "ORDER BY created_at DESC"
        
        # Get Reddit posts from dedicated redditpost table
        cursor.execute(f"""
            SELECT id, title, author, subreddit, score, num_comments, 
                   created_at, link
            FROM redditpost 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
            {order_clause}
            LIMIT 50
        """)
        
        posts = []
        for row in cursor.fetchall():
            # Calculate engagement score
            engagement_score = (row[4] or 0) + (row[5] or 0) * 2
            
            posts.append({
                "id": row[0],
                "title": row[1],
                "content": "",  # No content field in current schema
                "author": row[2],
                "subreddit": row[3],
                "url": row[7],
                "score": row[4],
                "upvotes": row[4],  # Use score as upvotes
                "downvotes": 0,  # Not available in current schema
                "comments": row[5],
                "shares": 0,  # Not available in current schema
                "gilded": 0,  # Not available in current schema
                "is_original_content": False,  # Not available in current schema
                "engagement_score": engagement_score,
                "published_at": row[6].isoformat() if row[6] else None
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(posts)
        
    except Exception as e:
        logger.error(f"Error getting Reddit posts: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False) 