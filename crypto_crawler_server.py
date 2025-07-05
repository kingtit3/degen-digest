#!/usr/bin/env python3
"""
Crypto Crawler Server
Web server wrapper for the Crypto crawler to run on Google Cloud Run
"""

import asyncio
import os
import threading

from flask import Flask, jsonify

from crypto_crawler import CryptoCrawler

app = Flask(__name__)

# Global variables to track crawler status
crawler_running = False
crawler_thread = None


def run_crypto_crawler():
    """Run the Crypto crawler in a separate thread"""
    global crawler_running

    try:
        print("🚀 Starting Crypto crawler...")
        crawler_running = True

        # Create crawler instance and run
        crawler = CryptoCrawler()
        result = asyncio.run(crawler.run_single_crawl())

        print("✅ Crypto crawler completed successfully")
        print(f"📊 Collected {len(result.get('gainers', []))} items")

    except Exception as e:
        print(f"❌ Error running Crypto crawler: {e}")
    finally:
        crawler_running = False


@app.route("/")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "service": "crypto-crawler",
            "crawler_running": crawler_running,
        }
    )


@app.route("/crawl", methods=["POST"])
def start_crawl():
    """Start the Crypto crawler"""
    global crawler_thread, crawler_running

    if crawler_running:
        return jsonify(
            {"status": "running", "message": "Crypto crawler is already running"}
        )

    crawler_thread = threading.Thread(target=run_crypto_crawler, daemon=True)
    crawler_thread.start()

    return jsonify(
        {"status": "started", "message": "Crypto crawler started successfully"}
    )


@app.route("/status")
def get_status():
    """Get crawler status"""
    return jsonify(
        {
            "status": "running" if crawler_running else "stopped",
            "crawler_running": crawler_running,
            "service": "crypto-crawler",
        }
    )


if __name__ == "__main__":
    # Get port from environment variable (Cloud Run sets PORT)
    port = int(os.environ.get("PORT", 8080))

    print(f"🌐 Starting Crypto crawler server on port {port}")
    print("📱 Endpoints:")
    print("   GET  /         - Health check")
    print("   POST /crawl    - Start crawler")
    print("   GET  /status   - Get status")

    # Start the Flask server
    app.run(host="0.0.0.0", port=port, debug=False)
