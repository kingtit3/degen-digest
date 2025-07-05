#!/usr/bin/env python3
"""
News Crawler Server
Web server wrapper for the News crawler to run on Google Cloud Run
"""

import asyncio
import os
import threading

from flask import Flask, jsonify

from news_crawler import NewsCrawler

app = Flask(__name__)

# Global variables to track crawler status
crawler_running = False
crawler_thread = None


def run_news_crawler():
    """Run the News crawler in a separate thread"""
    global crawler_running

    try:
        print("🚀 Starting News crawler...")
        crawler_running = True

        # Create crawler instance and run
        crawler = NewsCrawler()
        result = asyncio.run(crawler.run_single_crawl())

        print("✅ News crawler completed successfully")
        print(f"📊 Collected {len(result.get('articles', []))} articles")

    except Exception as e:
        print(f"❌ Error running News crawler: {e}")
    finally:
        crawler_running = False


@app.route("/")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "service": "news-crawler",
            "crawler_running": crawler_running,
        }
    )


@app.route("/crawl", methods=["POST"])
def start_crawl():
    """Start the News crawler"""
    global crawler_thread, crawler_running

    if crawler_running:
        return jsonify(
            {"status": "running", "message": "News crawler is already running"}
        )

    crawler_thread = threading.Thread(target=run_news_crawler, daemon=True)
    crawler_thread.start()

    return jsonify(
        {"status": "started", "message": "News crawler started successfully"}
    )


@app.route("/status")
def get_status():
    """Get crawler status"""
    return jsonify(
        {
            "status": "running" if crawler_running else "stopped",
            "crawler_running": crawler_running,
            "service": "news-crawler",
        }
    )


if __name__ == "__main__":
    # Get port from environment variable (Cloud Run sets PORT)
    port = int(os.environ.get("PORT", 8080))

    print(f"🌐 Starting News crawler server on port {port}")
    print("📱 Endpoints:")
    print("   GET  /         - Health check")
    print("   POST /crawl    - Start crawler")
    print("   GET  /status   - Get status")

    # Start the Flask server
    app.run(host="0.0.0.0", port=port, debug=False)
