#!/usr/bin/env python3
"""
Debug script to test the migration process step by step
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

# Environment variables
DB_HOST = "34.9.71.174"
DB_PORT = 5432
DB_NAME = "degen_digest"
DB_USER = "postgres"
DB_PASSWORD = "DegenDigest2024!"
GCS_BUCKET = "degen-digest-data"
PROJECT_ID = "lucky-union-463615-t3"


def test_database_connection():
    """Test database connection"""
    try:
        logger.info("Testing database connection...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )

        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM data_sources")
            count = cursor.fetchone()[0]
            logger.info(f"Database connected successfully. Found {count} data sources.")

            cursor.execute("SELECT name FROM data_sources")
            sources = [row[0] for row in cursor.fetchall()]
            logger.info(f"Data sources: {sources}")

        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def test_gcs_connection():
    """Test GCS connection and list files"""
    try:
        logger.info("Testing GCS connection...")
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET)

        # List all consolidated files
        blobs = list(bucket.list_blobs(prefix="consolidated/"))
        logger.info(f"Found {len(blobs)} consolidated files in GCS:")

        for blob in blobs:
            logger.info(f"  - {blob.name} ({blob.size} bytes)")

        return True, blobs
    except Exception as e:
        logger.error(f"GCS connection failed: {e}")
        return False, []


def test_crypto_data():
    """Test specifically crypto data"""
    try:
        logger.info("Testing crypto data specifically...")
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET)

        # Check for crypto consolidated file
        crypto_blob = bucket.blob("consolidated/crypto_consolidated.json")
        if crypto_blob.exists():
            logger.info("Found crypto_consolidated.json")
            data = json.loads(crypto_blob.download_as_text())
            logger.info(f"Crypto data keys: {list(data.keys())}")

            # Check for tokens key
            if "tokens" in data:
                tokens = data["tokens"]
                logger.info(f"Found {len(tokens)} tokens")
                if tokens:
                    logger.info(f"Sample token: {tokens[0]}")
            else:
                logger.warning("No 'tokens' key found in crypto data")
                logger.info(f"Available keys: {list(data.keys())}")
        else:
            logger.warning("crypto_consolidated.json not found")

        return True
    except Exception as e:
        logger.error(f"Crypto data test failed: {e}")
        return False


def test_migration_step():
    """Test one step of the migration process"""
    try:
        logger.info("Testing migration step...")

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

        # Test with crypto data
        crypto_blob = bucket.blob("consolidated/crypto_consolidated.json")
        if not crypto_blob.exists():
            logger.error("Crypto consolidated file not found")
            return False

        data = json.loads(crypto_blob.download_as_text())
        source_name = "crypto"

        # Get source_id
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM data_sources WHERE name = %s", (source_name,)
            )
            result = cursor.fetchone()
            if not result:
                logger.error(f"Source {source_name} not found in database")
                return False
            source_id = result[0]
            logger.info(f"Found source_id: {source_id}")

            # Check data structure
            data_key = "tokens"
            items = data.get(data_key, [])
            logger.info(f"Found {len(items)} items in crypto data")

            if items:
                logger.info(f"Sample item keys: {list(items[0].keys())}")

        conn.close()
        return True
    except Exception as e:
        logger.error(f"Migration step test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("Starting migration debug tests...")

    # Test 1: Database connection
    if not test_database_connection():
        logger.error("Database connection failed. Stopping.")
        return

    # Test 2: GCS connection
    gcs_ok, blobs = test_gcs_connection()
    if not gcs_ok:
        logger.error("GCS connection failed. Stopping.")
        return

    # Test 3: Crypto data specifically
    if not test_crypto_data():
        logger.error("Crypto data test failed.")
        return

    # Test 4: Migration step
    if not test_migration_step():
        logger.error("Migration step test failed.")
        return

    logger.info("All tests completed successfully!")


if __name__ == "__main__":
    main()
