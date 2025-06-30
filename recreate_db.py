#!/usr/bin/env python3
"""Recreate the database with updated schema."""

from storage.db import SQLModel, engine

def main():
    print("Dropping all tables...")
    SQLModel.metadata.drop_all(engine)
    
    print("Creating all tables with new schema...")
    SQLModel.metadata.create_all(engine)
    
    print("Database recreated successfully!")

if __name__ == "__main__":
    main() 