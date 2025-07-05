#!/usr/bin/env python3
"""
Enhanced Twitter Crawler Server
Web server wrapper for the Twitter crawler with comprehensive logging and debugging
"""

import asyncio
import logging
import os
import threading
import time
from datetime import UTC, datetime, timezone

from flask import Flask, jsonify

from scrapers.twitter_playwright_enhanced import EnhancedTwitterPlaywrightCrawler

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables to track crawler status
crawler_running = False
crawler_thread = None
crawler_start_time = None
crawler_progress = {}


def log_step(step_name: str, message: str, level: str = "info"):
    """Log a step with timestamp and progress tracking"""
    timestamp = datetime.now(UTC).isoformat()
    log_msg = f"🔍 [{step_name}] {message}"

    if level == "error":
        logger.error(log_msg)
    elif level == "warning":
        logger.warning(log_msg)
    else:
        logger.info(log_msg)

    # Update progress tracking
    crawler_progress[step_name] = {
        "timestamp": timestamp,
        "message": message,
        "status": level,
    }

    print(f"📝 {log_msg}")


def run_twitter_crawler():
    """Run the Twitter crawler in a separate thread with comprehensive logging"""
    global crawler_running, crawler_start_time, crawler_progress

    try:
        crawler_start_time = datetime.now(UTC)
        crawler_progress = {}
        log_step(
            "START",
            "🚀 Starting enhanced Twitter crawler with comprehensive logging...",
        )
        crawler_running = True

        # Step 1: Check environment variables
        log_step("ENV_CHECK", "Checking environment variables...")
        username = os.environ.get("TWITTER_USERNAME")
        password = os.environ.get("TWITTER_PASSWORD")

        if not username or not password:
            log_step(
                "ENV_CHECK",
                "❌ Twitter credentials not found in environment variables",
                "error",
            )
            return

        log_step("ENV_CHECK", f"✅ Twitter credentials found for user: {username}")

        # Step 2: Create crawler instance
        log_step(
            "CRAWLER_INIT", "Creating EnhancedTwitterPlaywrightCrawler instance..."
        )
        try:
            crawler = EnhancedTwitterPlaywrightCrawler(
                username=username,
                password=password,
                headless=True,  # Ensure headless mode for cloud
            )
            log_step("CRAWLER_INIT", "✅ Crawler instance created successfully")
        except Exception as e:
            log_step(
                "CRAWLER_INIT", f"❌ Failed to create crawler instance: {e}", "error"
            )
            return

        # Step 3: Run crawl with timeout and detailed logging
        log_step("CRAWL_START", "Starting crawl session with 10-minute timeout...")

        # Set a reasonable timeout for the entire crawl process
        async def run_crawl_with_timeout():
            try:
                log_step(
                    "BROWSER_SETUP", "Setting up browser (this may take 1-2 minutes)..."
                )

                # Try to setup browser with retry logic
                max_browser_retries = 3
                browser_setup_success = False

                for attempt in range(max_browser_retries):
                    try:
                        await crawler.setup_browser()
                        browser_setup_success = True
                        log_step(
                            "BROWSER_SETUP",
                            f"✅ Browser setup successful on attempt {attempt + 1}",
                        )
                        break
                    except Exception as e:
                        log_step(
                            "BROWSER_SETUP",
                            f"❌ Browser setup failed on attempt {attempt + 1}: {str(e)[:100]}...",
                            "error",
                        )
                        if attempt < max_browser_retries - 1:
                            log_step(
                                "BROWSER_SETUP",
                                "🔄 Retrying browser setup in 10 seconds...",
                            )
                            await asyncio.sleep(10)
                        else:
                            log_step(
                                "BROWSER_SETUP",
                                "❌ All browser setup attempts failed",
                                "error",
                            )
                            return []

                if not browser_setup_success:
                    log_step(
                        "BROWSER_SETUP",
                        "❌ Cannot proceed without browser setup",
                        "error",
                    )
                    return []

                # Now try to run the crawl
                log_step("CRAWL_EXECUTION", "Starting tweet collection...")
                result = await crawler.run_single_crawl(
                    max_tweets_per_query=5
                )  # Reduced for testing
                log_step(
                    "CRAWL_COMPLETE",
                    f"✅ Crawl completed successfully! Collected {len(result)} tweets",
                )
                return result

            except TimeoutError:
                log_step(
                    "CRAWL_TIMEOUT", "❌ Crawl timed out after 10 minutes", "error"
                )
                return []
            except Exception as e:
                log_step(
                    "CRAWL_ERROR",
                    f"❌ Crawl failed with error: {str(e)[:200]}...",
                    "error",
                )
                return []
            finally:
                # Always cleanup browser resources
                try:
                    await crawler.cleanup()
                    log_step("CLEANUP", "✅ Browser cleanup completed")
                except Exception as e:
                    log_step(
                        "CLEANUP",
                        f"⚠️ Browser cleanup failed: {str(e)[:100]}...",
                        "warning",
                    )

        # Run with timeout
        try:
            result = asyncio.run(
                asyncio.wait_for(run_crawl_with_timeout(), timeout=600)
            )  # 10 minutes
        except TimeoutError:
            log_step("OVERALL_TIMEOUT", "❌ Overall crawl process timed out", "error")
            result = []
        except Exception as e:
            log_step("OVERALL_ERROR", f"❌ Overall crawl process failed: {e}", "error")
            result = []

        # Step 4: Process results
        if isinstance(result, list):
            tweet_count = len(result)
            log_step(
                "RESULTS", f"📊 Processing results: {tweet_count} tweets collected"
            )

            if tweet_count > 0:
                # Log sample tweet data for debugging
                sample_tweet = result[0] if result else {}
                log_step(
                    "SAMPLE_DATA",
                    f"Sample tweet keys: {list(sample_tweet.keys()) if sample_tweet else 'No tweets'}",
                )

                # Check if tweets have expected fields
                if sample_tweet:
                    has_text = "text" in sample_tweet
                    has_username = "username" in sample_tweet
                    has_timestamp = "timestamp" in sample_tweet
                    log_step(
                        "DATA_QUALITY",
                        f"Tweet quality check - Text: {has_text}, Username: {has_username}, Timestamp: {has_timestamp}",
                    )

            log_step(
                "FINAL",
                f"✅ Twitter crawler completed successfully! Collected {tweet_count} tweets",
            )
        else:
            log_step("RESULTS", f"⚠️ Unexpected result type: {type(result)}", "warning")
            tweet_count = 0

    except Exception as e:
        log_step("FATAL_ERROR", f"❌ Fatal error in Twitter crawler: {e}", "error")
        import traceback

        traceback.print_exc()
    finally:
        crawler_running = False
        end_time = datetime.now(UTC)
        duration = (end_time - crawler_start_time).total_seconds()
        log_step(
            "CLEANUP",
            f"🧹 Crawler cleanup completed. Total duration: {duration:.1f} seconds",
        )


@app.route("/")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "service": "twitter-crawler",
            "crawler_running": crawler_running,
            "uptime": str(datetime.now(UTC) - crawler_start_time)
            if crawler_start_time
            else None,
        }
    )


@app.route("/crawl", methods=["POST"])
def start_crawl():
    """Start the Twitter crawler"""
    global crawler_thread, crawler_running

    if crawler_running:
        return jsonify(
            {
                "status": "running",
                "message": "Twitter crawler is already running",
                "start_time": crawler_start_time.isoformat()
                if crawler_start_time
                else None,
            }
        )

    crawler_thread = threading.Thread(target=run_twitter_crawler, daemon=True)
    crawler_thread.start()

    return jsonify(
        {
            "status": "started",
            "message": "Enhanced Twitter crawler started with comprehensive logging",
            "start_time": datetime.now(UTC).isoformat(),
        }
    )


@app.route("/status")
def get_status():
    """Get detailed crawler status"""
    return jsonify(
        {
            "status": "running" if crawler_running else "stopped",
            "crawler_running": crawler_running,
            "service": "twitter-crawler",
            "start_time": crawler_start_time.isoformat()
            if crawler_start_time
            else None,
            "progress": crawler_progress,
        }
    )


@app.route("/logs")
def get_logs():
    """Get recent crawler logs"""
    return jsonify(
        {
            "service": "twitter-crawler",
            "logs": crawler_progress,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )


if __name__ == "__main__":
    # Get port from environment variable (Cloud Run sets PORT)
    port = int(os.environ.get("PORT", 8080))

    print(f"🌐 Starting Enhanced Twitter crawler server on port {port}")
    print("📱 Endpoints:")
    print("   GET  /         - Health check")
    print("   POST /crawl    - Start crawler")
    print("   GET  /status   - Get detailed status")
    print("   GET  /logs     - Get crawler logs")

    # Start the Flask server
    app.run(host="0.0.0.0", port=port, debug=False)
