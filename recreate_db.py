#!/usr/bin/env python3
"""
Script to recreate the database with the correct schema
"""

import os
import shutil
import time
from pathlib import Path
from storage.db import engine
from sqlmodel import SQLModel

def recreate_database():
    """Recreate the database with the correct schema"""
    
    # Backup existing database
    db_path = Path("output/degen_digest.db")
    if db_path.exists():
        backup_path = Path(f"output/degen_digest.backup.{int(time.time())}.db")
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backed up existing database to {backup_path}")
    
    # Remove existing database
    if db_path.exists():
        db_path.unlink()
        print("🗑️ Removed existing database")
    
    # Create new database with correct schema
    SQLModel.metadata.create_all(engine)
    print("✅ Created new database with correct schema")
    
    # Verify tables were created
    from sqlmodel import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📋 Created tables: {tables}")
    
    # Show schema for verification
    for table in tables:
        print(f"\n📊 Table: {table}")
        columns = inspector.get_columns(table)
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

if __name__ == "__main__":
    print("🔄 Recreating database with correct schema...")
    recreate_database()
    print("✅ Database recreation complete!") 