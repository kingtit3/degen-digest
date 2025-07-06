#!/usr/bin/env python3
"""
FarmChecker.xyz API Server - Temporary version without CORS
Connects to Cloud SQL and serves data to the frontend
"""

import json

# from flask_cors import CORS  # Commented out temporarily
import logging
import os
from datetime import datetime, timedelta

import psycopg2
from flask import Flask, jsonify, request, send_from_directory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# CORS(app)  # Commented out temporarily

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


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(".", filename)


@app.route("/api/test")
def test_api():
    """Simple test endpoint"""
    return jsonify(
        {
            "status": "success",
            "message": "Server is running!",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/system-status")
def get_system_status():
    """Get system status"""
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            db_status = "connected"
        else:
            db_status = "disconnected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify(
        {
            "status": "running",
            "database": db_status,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }
    )


if __name__ == "__main__":
    print("Starting FarmChecker server...")
    print(
        "Database config:",
        {k: v if k != "password" else "***" for k, v in DB_CONFIG.items()},
    )
    app.run(host="0.0.0.0", port=8080, debug=True)
