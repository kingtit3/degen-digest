#!/usr/bin/env python3
"""
Simple data migration script - run manually when needed
"""
import json
import logging
import os
from datetime import datetime

import psycopg2
from google.cloud import storage
from psycopg2.extras import RealDictCursor

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
DB_HOST = "34.9.71.174"
DB_PORT = 5432
DB_NAME = "degen_digest"
DB_USER = "postgres"
DB_PASSWORD = "DegenDigest2024!"
GCS_BUCKET = "degen-digest-data"
PROJECT_ID = "lucky-union-463615-t3"

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

        # Print summary
        logger.info("🎉 Migration completed!")
        logger.info(f"📈 Total items imported: {total_imported}")
        logger.info("📊 Breakdown by source:")
        for source, count in source_stats.items():
            logger.info(f"   {source}: {count} items")

        return total_imported, source_stats

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    try:
        total, stats = migrate_data()
        print(f"\n✅ Migration successful! Total: {total} items")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        exit(1)
