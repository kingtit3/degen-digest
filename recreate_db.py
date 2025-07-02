#!/usr/bin/env python3
"""Recreate the database with the correct schema."""

import shutil
from datetime import datetime
from pathlib import Path


def recreate_database():
    """Recreate the database with the correct schema."""

    # Database paths
    db_path = Path("output/degen_digest.db")
    backup_dir = Path("output/backups")
    backup_dir.mkdir(exist_ok=True)

    # Create backup if database exists
    if db_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"degen_digest_backup_{timestamp}.db"
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")

        # Remove the old database
        db_path.unlink()
        print("🗑️  Old database removed")

    # Import and initialize the new database
    try:
        from storage.db import SQLModel, engine

        # Create all tables with the new schema
        SQLModel.metadata.create_all(engine)
        print("✅ Database recreated with correct schema")

        # Verify the database was created
        if db_path.exists():
            print(f"✅ Database file created at: {db_path}")
            print(f"📊 Database size: {db_path.stat().st_size} bytes")
        else:
            print("❌ Database file was not created")

    except Exception as e:
        print(f"❌ Error recreating database: {e}")
        return False

    return True


def verify_schema():
    """Verify the database schema is correct."""
    try:
        from sqlmodel import Session, select

        from storage.db import Digest, LLMUsage, RedditPost, Tweet, TweetMetrics, engine

        with Session(engine) as session:
            # Test each table
            tables = [Tweet, RedditPost, Digest, LLMUsage, TweetMetrics]

            for table in tables:
                try:
                    # Try to query the table
                    session.exec(select(table)).limit(1).all()
                    print(f"✅ {table.__name__}: Schema verified")
                except Exception as e:
                    print(f"❌ {table.__name__}: Schema error - {e}")
                    return False

        print("✅ All tables verified successfully")
        return True

    except Exception as e:
        print(f"❌ Error verifying schema: {e}")
        return False


if __name__ == "__main__":
    print("🔄 Recreating Degen Digest Database...")
    print("=" * 50)

    # Recreate database
    if recreate_database():
        print("\n🔍 Verifying database schema...")
        if verify_schema():
            print("\n🎉 Database recreation completed successfully!")
            print("\n📋 Next steps:")
            print("1. Run scrapers to collect new data")
            print("2. Generate a new digest")
            print("3. Start the dashboard")
        else:
            print("\n❌ Schema verification failed!")
    else:
        print("\n❌ Database recreation failed!")
