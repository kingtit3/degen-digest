#!/usr/bin/env python3
"""
Check and import crypto data from GCS to Cloud SQL
"""

import json
import os
from datetime import datetime

import psycopg2
from google.cloud import storage

# Database configuration
DB_CONFIG = {
    "host": "34.9.71.174",
    "database": "degen_digest",
    "user": "postgres",
    "password": "DegenDigest2024!",
    "port": "5432",
}

# GCS configuration
GCS_BUCKET = "degen-digest-data"
PROJECT_ID = "lucky-union-463615-t3"


def check_database():
    """Check what crypto data is in the database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Check crypto sources
        cursor.execute(
            """
            SELECT ds.name, COUNT(*) as item_count
            FROM data_sources ds
            LEFT JOIN content_items ci ON ds.id = ci.source_id
            WHERE ds.name IN ('crypto', 'dexpaprika', 'dexscreener')
            GROUP BY ds.name
        """
        )

        results = cursor.fetchall()
        print("📊 Current crypto data in database:")
        for name, count in results:
            print(f"  - {name}: {count} items")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Database error: {e}")


def check_gcs():
    """Check what crypto data is in GCS"""
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET)

        crypto_files = [
            "consolidated/crypto_consolidated.json",
            "consolidated/dexpaprika_consolidated.json",
            "consolidated/dexscreener_consolidated.json",
        ]

        print("\n📁 Checking GCS files:")
        for file_path in crypto_files:
            blob = bucket.blob(file_path)
            if blob.exists():
                print(f"  ✅ {file_path} exists ({blob.size} bytes)")
                # Try to read a sample
                try:
                    content = blob.download_as_text()
                    data = json.loads(content)
                    if "tokens" in data:
                        print(f"    - Contains {len(data['tokens'])} tokens")
                    elif "data" in data:
                        print(f"    - Contains {len(data['data'])} items")
                    else:
                        print(f"    - Contains keys: {list(data.keys())}")
                except Exception as e:
                    print(f"    - Error reading file: {e}")
            else:
                print(f"  ❌ {file_path} does not exist")

    except Exception as e:
        print(f"❌ GCS error: {e}")


if __name__ == "__main__":
    print("🔍 Checking crypto data status...")
    check_database()
    check_gcs()
