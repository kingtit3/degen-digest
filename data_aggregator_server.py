#!/usr/bin/env python3
"""
Data Aggregator Server
Web server wrapper for the Data Aggregator to run on Google Cloud Run
"""

import asyncio
import os
import threading

from flask import Flask, jsonify

from data_aggregator import DataAggregator

app = Flask(__name__)

# Global variables to track aggregator status
aggregator_running = False
aggregator_thread = None


def run_data_aggregator():
    """Run the Data Aggregator in a separate thread"""
    global aggregator_running

    try:
        print("🚀 Starting Data Aggregator...")
        aggregator_running = True

        # Create aggregator instance and run
        aggregator = DataAggregator()
        result = asyncio.run(aggregator.run_aggregation())

        print("✅ Data Aggregator completed successfully")

        # Print summary
        total_items = (
            len(result.get("twitter", {}).get("posts", []))
            + len(result.get("reddit", {}).get("posts", []))
            + len(result.get("news", {}).get("articles", []))
            + len(result.get("crypto", {}).get("gainers", []))
        )
        print(f"📊 Total items consolidated: {total_items}")

    except Exception as e:
        print(f"❌ Error running Data Aggregator: {e}")
    finally:
        aggregator_running = False


@app.route("/")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "service": "data-aggregator",
            "aggregator_running": aggregator_running,
        }
    )


@app.route("/aggregate", methods=["POST"])
def start_aggregation():
    """Start the Data Aggregator"""
    global aggregator_thread, aggregator_running

    if aggregator_running:
        return jsonify(
            {"status": "running", "message": "Data Aggregator is already running"}
        )

    aggregator_thread = threading.Thread(target=run_data_aggregator, daemon=True)
    aggregator_thread.start()

    return jsonify(
        {"status": "started", "message": "Data Aggregator started successfully"}
    )


@app.route("/status")
def get_status():
    """Get aggregator status"""
    return jsonify(
        {
            "status": "running" if aggregator_running else "stopped",
            "aggregator_running": aggregator_running,
            "service": "data-aggregator",
        }
    )


if __name__ == "__main__":
    # Get port from environment variable (Cloud Run sets PORT)
    port = int(os.environ.get("PORT", 8080))

    print(f"🌐 Starting Data Aggregator server on port {port}")
    print("📱 Endpoints:")
    print("   GET  /           - Health check")
    print("   POST /aggregate  - Start aggregation")
    print("   GET  /status     - Get status")

    # Start the Flask server
    app.run(host="0.0.0.0", port=port, debug=False)
