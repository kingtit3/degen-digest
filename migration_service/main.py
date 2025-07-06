#!/usr/bin/env python3
"""
Robust Migration Service for Cloud Run
"""
import json
import logging
import os
from datetime import datetime

import psycopg2
from flask import Flask, jsonify, request
from google.cloud import storage
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
DB_HOST = os.getenv("DB_HOST", "34.9.71.174")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "degen_digest")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "DegenDigest2024!")
GCS_BUCKET = os.getenv("BUCKET_NAME", "degen-digest-data")
PROJECT_ID = os.getenv("PROJECT_ID", "lucky-union-463615-t3")

# Source mapping for data keys
DATA_KEYS = {
    "reddit": "posts",
    "twitter": "tweets",
    "news": "articles",
    "crypto": "gainers",
    "dexpaprika": "token_data",
    "dexscreener": "latest_token_profiles",
}


def safe_string(value):
    """Safely convert value to string, handling None and dict types"""
    if value is None:
        return None
    if isinstance(value, dict):
        return json.dumps(value)
    return str(value)


def extract_items_from_data(data, source_name):
    """Extract items from data based on source-specific logic"""
    items = []

    if source_name == "crypto":
        items = data.get("gainers", [])
    elif source_name == "dexpaprika":
        items = data.get("token_data", [])
    elif source_name == "dexscreener":
        items = []
        items.extend(data.get("latest_token_profiles", []))
        items.extend(data.get("latest_boosted_tokens", []))
        items.extend(data.get("top_boosted_tokens", []))
        items.extend(data.get("token_pairs", []))
    else:
        data_key = DATA_KEYS.get(source_name, "data")
        items = data.get(data_key, [])
        if not items and data_key != "data":
            items = data.get("data", [])

    return items


def test_database_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def test_gcs_connection():
    """Test GCS connection"""
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET)
        # Try to list blobs to test connection
        list(bucket.list_blobs(prefix="consolidated/", max_results=1))
        return True
    except Exception as e:
        logger.error(f"GCS connection failed: {e}")
        return False


def migrate_data():
    """Migrate data from GCS to Cloud SQL"""
    try:
        logger.info("🚀 Starting data migration...")

        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )

        # Connect to GCS
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET)

        # Get consolidated files
        blobs = list(bucket.list_blobs(prefix="consolidated/"))
        logger.info(f"📁 Found {len(blobs)} consolidated files")

        total_imported = 0
        source_stats = {}

        for blob in blobs:
            if not blob.name.endswith(".json"):
                continue

            source_name = blob.name.split("/")[-1].replace("_consolidated.json", "")
            logger.info(f"📊 Processing {source_name}...")

            try:
                data = json.loads(blob.download_as_text())

                # Get source_id
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM data_sources WHERE name = %s", (source_name,)
                    )
                    result = cursor.fetchone()
                    if not result:
                        logger.warning(f"⚠️  Source {source_name} not found in database")
                        continue
                    source_id = result[0]

                    # Extract items
                    items = extract_items_from_data(data, source_name)
                    logger.info(f"   Found {len(items)} items")

                    if not items:
                        logger.warning(f"   No items found for {source_name}")
                        continue

                    # Insert collection
                    cursor.execute(
                        """
                        INSERT INTO data_collections (source_id, collection_timestamp, file_path, record_count, file_size_bytes)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """,
                        (source_id, datetime.now(), blob.name, len(items), blob.size),
                    )
                    collection_id = cursor.fetchone()[0]

                    # Insert content items
                    imported_count = 0
                    for item in items:
                        try:
                            external_id = safe_string(
                                item.get("id")
                                or item.get("external_id")
                                or item.get("address")
                                or item.get("pair_id")
                            )
                            title = safe_string(
                                item.get("title")
                                or item.get("name")
                                or item.get("symbol")
                                or str(item.get("price_change", ""))[:500]
                            )
                            content = safe_string(
                                item.get("content")
                                or item.get("summary")
                                or item.get("description")
                                or str(item)
                            )
                            author = safe_string(
                                item.get("author")
                                or item.get("username")
                                or item.get("creator")
                            )
                            url = safe_string(
                                item.get("url")
                                or item.get("link")
                                or item.get("website")
                            )
                            published_at = (
                                item.get("published_at")
                                or item.get("created_at")
                                or item.get("published")
                                or item.get("timestamp")
                            )

                            cursor.execute(
                                """
                                INSERT INTO content_items (collection_id, source_id, external_id, title, content, author, url, published_at, raw_data)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT DO NOTHING
                            """,
                                (
                                    collection_id,
                                    source_id,
                                    external_id,
                                    title,
                                    content,
                                    author,
                                    url,
                                    published_at,
                                    json.dumps(item),
                                ),
                            )
                            imported_count += 1
                        except Exception as e:
                            logger.error(f"   Error inserting item: {e}")
                            continue

                    source_stats[source_name] = imported_count
                    total_imported += imported_count
                    logger.info(f"   ✅ Imported {imported_count} items")

                conn.commit()

            except Exception as e:
                logger.error(f"   ❌ Error processing {source_name}: {e}")
                continue

        conn.close()

        logger.info("🎉 Migration completed!")
        logger.info(f"📈 Total items imported: {total_imported}")

        return total_imported, source_stats

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_ok = test_database_connection()
        gcs_ok = test_gcs_connection()

        if db_ok and gcs_ok:
            return (
                jsonify(
                    {
                        "status": "healthy",
                        "database": "connected",
                        "gcs": "connected",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "status": "unhealthy",
                        "database": "connected" if db_ok else "disconnected",
                        "gcs": "connected" if gcs_ok else "disconnected",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                503,
            )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/migrate", methods=["POST"])
def migrate_endpoint():
    """Migration endpoint"""
    try:
        logger.info("Received migration request")

        # Run migration
        total_imported, source_stats = migrate_data()

        return (
            jsonify(
                {
                    "status": "success",
                    "total_imported": total_imported,
                    "source_stats": source_stats,
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Migration endpoint error: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/", methods=["GET"])
def root():
    """Root endpoint"""
    return (
        jsonify(
            {
                "service": "migration-service",
                "version": "1.0.0",
                "endpoints": {"health": "/health", "migrate": "/migrate (POST)"},
                "timestamp": datetime.now().isoformat(),
            }
        ),
        200,
    )


if __name__ == "__main__":
    # Run with gunicorn for production
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
