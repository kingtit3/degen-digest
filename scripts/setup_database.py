#!/usr/bin/env python3
"""
Database Setup and Migration Script
Creates SQL database schema and migrates data from GCS
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Database imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print(
        "Warning: PostgreSQL not available. Install with: pip install psycopg2-binary"
    )

# Google Cloud Storage imports
try:
    from google.cloud import storage

    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("Warning: Google Cloud Storage not available")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    def __init__(
        self,
        db_config: dict[str, str] = None,
        gcs_bucket: str = "degen-digest-data",
        project_id: str = "lucky-union-463615-t3",
    ):
        self.db_config = db_config or {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_NAME", "degen_digest"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", ""),
        }

        self.gcs_bucket_name = gcs_bucket
        self.project_id = project_id
        self.gcs_client = None
        self.gcs_bucket = None
        self.db_connection = None

        # Initialize GCS
        if GCS_AVAILABLE:
            try:
                self.gcs_client = storage.Client(project=project_id)
                self.gcs_bucket = self.gcs_client.bucket(gcs_bucket)
                logger.info(f"GCS initialized: {gcs_bucket}")
            except Exception as e:
                logger.error(f"GCS initialization failed: {e}")

    def get_db_connection(self):
        """Get database connection"""
        if not DB_AVAILABLE:
            return None

        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None

    def create_schema(self):
        """Create database schema"""
        conn = self.get_db_connection()
        if not conn:
            logger.error("Cannot create schema - no database connection")
            return False

        try:
            with conn.cursor() as cursor:
                # Create data_sources table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS data_sources (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50) UNIQUE NOT NULL,
                        display_name VARCHAR(100) NOT NULL,
                        is_active BOOLEAN DEFAULT true,
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """
                )

                # Create data_collections table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS data_collections (
                        id SERIAL PRIMARY KEY,
                        source_id INTEGER REFERENCES data_sources(id),
                        collection_timestamp TIMESTAMP NOT NULL,
                        file_path VARCHAR(500) NOT NULL,
                        record_count INTEGER DEFAULT 0,
                        file_size_bytes BIGINT DEFAULT 0,
                        status VARCHAR(20) DEFAULT 'processed',
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """
                )

                # Create content_items table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS content_items (
                        id SERIAL PRIMARY KEY,
                        collection_id INTEGER REFERENCES data_collections(id),
                        source_id INTEGER REFERENCES data_sources(id),
                        external_id VARCHAR(255),
                        title TEXT,
                        content TEXT,
                        author VARCHAR(255),
                        url VARCHAR(1000),
                        published_at TIMESTAMP,
                        engagement_score DECIMAL(10,4),
                        virality_score DECIMAL(10,4),
                        sentiment_score DECIMAL(5,4),
                        raw_data JSONB,
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """
                )

                # Create crypto_tokens table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS crypto_tokens (
                        id SERIAL PRIMARY KEY,
                        symbol VARCHAR(20) NOT NULL,
                        name VARCHAR(100),
                        network VARCHAR(50),
                        contract_address VARCHAR(255),
                        market_cap DECIMAL(20,2),
                        price_usd DECIMAL(20,8),
                        volume_24h DECIMAL(20,2),
                        price_change_24h DECIMAL(10,4),
                        first_seen_at TIMESTAMP DEFAULT NOW(),
                        last_updated_at TIMESTAMP DEFAULT NOW()
                    );
                """
                )

                # Create token_mentions table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS token_mentions (
                        id SERIAL PRIMARY KEY,
                        content_item_id INTEGER REFERENCES content_items(id),
                        token_id INTEGER REFERENCES crypto_tokens(id),
                        mention_count INTEGER DEFAULT 1,
                        sentiment_score DECIMAL(5,4),
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """
                )

                # Create trending_topics table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS trending_topics (
                        id SERIAL PRIMARY KEY,
                        topic_name VARCHAR(255) NOT NULL,
                        source_id INTEGER REFERENCES data_sources(id),
                        mention_count INTEGER DEFAULT 0,
                        engagement_score DECIMAL(10,4),
                        trend_period_start TIMESTAMP,
                        trend_period_end TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """
                )

                # Insert default data sources
                cursor.execute(
                    """
                    INSERT INTO data_sources (name, display_name) VALUES
                    ('twitter', 'Twitter'),
                    ('reddit', 'Reddit'),
                    ('news', 'News'),
                    ('crypto', 'Crypto'),
                    ('telegram', 'Telegram'),
                    ('dexpaprika', 'DexPaprika'),
                    ('dexscreener', 'DexScreener')
                    ON CONFLICT (name) DO NOTHING;
                """
                )

                conn.commit()
                logger.info("✅ Database schema created successfully")
                return True

        except Exception as e:
            logger.error(f"❌ Schema creation failed: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def migrate_consolidated_data(self):
        """Migrate consolidated data from GCS"""
        if not self.gcs_bucket:
            logger.error("GCS not available")
            return False

        conn = self.get_db_connection()
        if not conn:
            logger.error("Database not available")
            return False

        try:
            # Get consolidated files
            consolidated_blobs = list(
                self.gcs_bucket.list_blobs(prefix="consolidated/")
            )

            for blob in consolidated_blobs:
                if not blob.name.endswith(".json"):
                    continue

                logger.info(f"Processing {blob.name}")

                # Download and parse data
                data = json.loads(blob.download_as_text())

                # Extract source name from filename
                source_name = blob.name.split("/")[-1].replace("_consolidated.json", "")

                # Get source ID
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM data_sources WHERE name = %s", (source_name,)
                    )
                    result = cursor.fetchone()
                    if not result:
                        logger.warning(f"Source {source_name} not found in database")
                        continue
                    source_id = result[0]

                # Determine the correct data key based on source
                data_key = "data"
                if source_name == "reddit":
                    data_key = "posts"
                elif source_name == "twitter":
                    data_key = "tweets"
                elif source_name == "news":
                    data_key = "articles"
                elif source_name == "crypto":
                    data_key = "tokens"

                items = data.get(data_key, [])
                if not items and data_key != "data":
                    # Fallback to 'data' if the specific key doesn't exist
                    items = data.get("data", [])

                # Create collection record and insert content items in the same cursor context
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO data_collections
                        (source_id, collection_timestamp, file_path, record_count, file_size_bytes)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """,
                        (source_id, datetime.now(), blob.name, len(items), blob.size),
                    )
                    collection_id = cursor.fetchone()[0]

                    # Insert content items (keep inside the same cursor context)
                    for item in items:
                        self._insert_content_item(
                            cursor, collection_id, source_id, item
                        )

                conn.commit()
                logger.info(f"✅ Migrated {blob.name}")

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def _insert_content_item(
        self, cursor, collection_id: int, source_id: int, item: dict[str, Any]
    ):
        """Insert a content item into the database"""
        try:
            cursor.execute(
                """
                INSERT INTO content_items
                (collection_id, source_id, external_id, title, content, author, url, published_at, raw_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    collection_id,
                    source_id,
                    item.get("id") or item.get("external_id"),
                    item.get("title") or item.get("text", "")[:500],
                    item.get("content") or item.get("text", ""),
                    item.get("author") or item.get("username"),
                    item.get("url"),
                    item.get("published_at") or item.get("created_at"),
                    json.dumps(item),
                ),
            )
        except Exception as e:
            logger.warning(f"Failed to insert content item: {e}")

    def get_migration_stats(self):
        """Get migration statistics"""
        conn = self.get_db_connection()
        if not conn:
            return None

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get counts
                cursor.execute("SELECT COUNT(*) as count FROM content_items")
                content_count = cursor.fetchone()["count"]

                cursor.execute("SELECT COUNT(*) as count FROM data_collections")
                collection_count = cursor.fetchone()["count"]

                cursor.execute("SELECT COUNT(*) as count FROM crypto_tokens")
                token_count = cursor.fetchone()["count"]

                # Get source breakdown
                cursor.execute(
                    """
                    SELECT ds.name, COUNT(ci.id) as count
                    FROM data_sources ds
                    LEFT JOIN content_items ci ON ds.id = ci.source_id
                    GROUP BY ds.id, ds.name
                    ORDER BY count DESC
                """
                )
                source_breakdown = cursor.fetchall()

                return {
                    "content_items": content_count,
                    "collections": collection_count,
                    "tokens": token_count,
                    "source_breakdown": source_breakdown,
                }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return None
        finally:
            conn.close()


def main():
    """Main migration function"""
    print("🚀 Starting Database Migration")
    print("=" * 50)

    # Initialize migrator
    migrator = DatabaseMigrator()

    # Create schema
    print("\n📋 Creating database schema...")
    if not migrator.create_schema():
        print("❌ Schema creation failed")
        return

    # Migrate data
    print("\n📦 Migrating consolidated data...")
    if not migrator.migrate_consolidated_data():
        print("❌ Data migration failed")
        return

    # Get stats
    print("\n📊 Migration Statistics:")
    stats = migrator.get_migration_stats()
    if stats:
        print(f"   Content Items: {stats['content_items']}")
        print(f"   Collections: {stats['collections']}")
        print(f"   Tokens: {stats['tokens']}")
        print("\n   Source Breakdown:")
        for source in stats["source_breakdown"]:
            print(f"     {source['name']}: {source['count']} items")

    print("\n✅ Migration completed successfully!")


if __name__ == "__main__":
    main()
