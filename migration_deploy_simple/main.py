import json
import logging
import os
from datetime import datetime

import functions_framework
import psycopg2
from google.cloud import storage
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
GCS_BUCKET = os.getenv("BUCKET_NAME", "degen-digest-data")
PROJECT_ID = os.getenv("PROJECT_ID")

# Source mapping for data keys - updated based on actual data structure
DATA_KEYS = {
    "reddit": "posts",
    "twitter": "tweets",
    "news": "articles",
    "crypto": "gainers",  # Changed from 'tokens' to 'gainers'
    "dexpaprika": "token_data",  # Added specific key for dexpaprika
    "dexscreener": "latest_token_profiles",  # Added specific key for dexscreener
    # fallback: 'data'
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
        # Crypto has 'gainers' key
        items = data.get("gainers", [])
    elif source_name == "dexpaprika":
        # DexPaprika has 'token_data' key
        items = data.get("token_data", [])
    elif source_name == "dexscreener":
        # DexScreener has multiple relevant keys
        items = []
        # Add latest token profiles
        items.extend(data.get("latest_token_profiles", []))
        # Add latest boosted tokens
        items.extend(data.get("latest_boosted_tokens", []))
        # Add top boosted tokens
        items.extend(data.get("top_boosted_tokens", []))
        # Add token pairs
        items.extend(data.get("token_pairs", []))
    else:
        # Default behavior for other sources
        data_key = DATA_KEYS.get(source_name, "data")
        items = data.get(data_key, [])
        if not items and data_key != "data":
            items = data.get("data", [])

    return items


@functions_framework.http
def migrate(request):
    """HTTP Cloud Function for migrating data from GCS to Cloud SQL."""
    try:
        logger.info("Starting robust migration to Cloud SQL...")

        # Connect to Cloud SQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )

        # GCS client
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET)

        # Get all consolidated files
        blobs = list(bucket.list_blobs(prefix="consolidated/"))
        logger.info(f"Found {len(blobs)} consolidated files.")

        imported = 0
        for blob in blobs:
            if not blob.name.endswith(".json"):
                continue
            logger.info(f"Processing {blob.name}")
            data = json.loads(blob.download_as_text())
            source_name = blob.name.split("/")[-1].replace("_consolidated.json", "")

            # Get source_id
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM data_sources WHERE name = %s", (source_name,)
                )
                result = cursor.fetchone()
                if not result:
                    logger.warning(f"Source {source_name} not found in database")
                    continue
                source_id = result[0]

                # Extract items using source-specific logic
                items = extract_items_from_data(data, source_name)
                logger.info(f"Found {len(items)} items for {source_name}")

                if not items:
                    logger.warning(f"No items found for {source_name}")
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
                for item in items:
                    try:
                        # Handle different item structures with safe string conversion
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
                            item.get("url") or item.get("link") or item.get("website")
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
                    except Exception as e:
                        logger.error(f"Error inserting item: {e}")
                        logger.error(f"Item data: {item}")
                        continue
                imported += len(items)
            conn.commit()

        logger.info(f"Migration complete. Imported {imported} items.")
        conn.close()

        return (
            json.dumps(
                {
                    "status": "success",
                    "imported": imported,
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
            {"Content-Type": "application/json"},
        )

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return (
            json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
            {"Content-Type": "application/json"},
        )
