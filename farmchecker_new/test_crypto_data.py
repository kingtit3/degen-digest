#!/usr/bin/env python3
"""
Test script to check crypto data structure
"""

import json
import os

import psycopg2

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "34.9.71.174"),
    "database": os.getenv("DB_NAME", "degen_digest"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "DegenDigest2024!"),
    "port": os.getenv("DB_PORT", "5432"),
}


def test_crypto_data():
    """Test crypto data structure"""
    try:
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("✅ Database connection successful!")

        # Check crypto sources
        sources = ["crypto", "dexpaprika", "dexscreener"]

        for source in sources:
            print(f"\n📊 Checking {source} data...")

            cursor.execute(
                """
                SELECT ci.id, ci.title, ci.content, ci.raw_data
                FROM content_items ci
                JOIN data_sources ds ON ci.source_id = ds.id
                WHERE ds.name = %s
                LIMIT 3
            """,
                (source,),
            )

            rows = cursor.fetchall()
            print(f"Found {len(rows)} items for {source}")

            for i, row in enumerate(rows):
                print(f"\n--- Item {i+1} ---")
                print(f"ID: {row[0]}")
                print(f"Title: {row[1]}")
                print(f"Content: {row[2][:100]}..." if row[2] else "No content")

                if row[3]:  # raw_data
                    try:
                        data = json.loads(row[3]) if isinstance(row[3], str) else row[3]
                        print(
                            f"Raw data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}"
                        )

                        # Show first few key-value pairs
                        if isinstance(data, dict):
                            for key, value in list(data.items())[:5]:
                                if isinstance(value, (str, int, float)):
                                    print(f"  {key}: {value}")
                                else:
                                    print(f"  {key}: {type(value).__name__}")
                    except Exception as e:
                        print(f"Error parsing raw_data: {e}")

        cursor.close()
        conn.close()

        print("\n✅ Crypto data test complete!")
        return True

    except Exception as e:
        print(f"❌ Crypto data test failed: {e}")
        return False


if __name__ == "__main__":
    test_crypto_data()
