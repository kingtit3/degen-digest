#!/usr/bin/env python3
"""
Test script to verify database connectivity
"""

import os
from datetime import datetime

import psycopg2

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "34.9.71.174"),
    "database": os.getenv("DB_NAME", "degen_digest"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "DegenDigest2024!"),
    "port": os.getenv("DB_PORT", "5432"),
}


def test_connection():
    """Test database connection and basic queries"""
    try:
        print("🔌 Testing database connection...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("✅ Database connection successful!")

        # Test basic queries
        print("\n📊 Testing queries...")

        # Check content_items table
        cursor.execute("SELECT COUNT(*) FROM content_items")
        total_items = cursor.fetchone()[0]
        print(f"📝 Total content items: {total_items}")

        # Check by source
        cursor.execute(
            """
            SELECT ds.name, COUNT(*) FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            GROUP BY ds.name
        """
        )
        source_counts = cursor.fetchall()
        print("📈 Content by source:")
        for source, count in source_counts:
            print(f"  - {source}: {count}")

        # Check recent items
        cursor.execute(
            """
            SELECT ds.name, COUNT(*) FROM content_items ci
            JOIN data_sources ds ON ci.source_id = ds.id
            WHERE ci.created_at >= NOW() - INTERVAL '24 hours'
            GROUP BY ds.name
        """
        )
        recent_counts = cursor.fetchall()
        print("\n🕐 Recent content (last 24h):")
        for source, count in recent_counts:
            print(f"  - {source}: {count}")

        # Check digests
        cursor.execute("SELECT COUNT(*) FROM digests")
        digest_count = cursor.fetchone()[0]
        print(f"\n📰 Total digests: {digest_count}")

        # Get latest digest
        cursor.execute(
            """
            SELECT title, created_at FROM digests
            ORDER BY created_at DESC LIMIT 1
        """
        )
        latest = cursor.fetchone()
        if latest:
            print(f"📰 Latest digest: {latest[0]} ({latest[1]})")
        else:
            print("📰 No digests found")

        cursor.close()
        conn.close()

        print("\n✅ All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
