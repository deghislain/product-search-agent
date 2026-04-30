"""
Migration: Add query optimization fields to search_requests table
Date: 2026-04-26
Description: Adds fields for intelligent query refinement and optimization tracking

This migration adds three new columns to support the agentic query optimization feature:
- query_version: Tracks the number of times a query has been optimized
- query_history: Stores the history of query optimizations as JSON
- optimization_enabled: Flag to enable/disable automatic optimization

Usage:
    python backend/migrations/add_query_optimization_fields.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from app.config import settings


def upgrade():
    """Apply the migration."""
    print("🔄 Starting migration: Add query optimization fields...")
    
    # Use the backend database explicitly
    backend_db_path = os.path.join(os.path.dirname(__file__), '..', 'product_search.db')
    database_url = f"sqlite:///{backend_db_path}"
    
    print(f"📍 Using database: {backend_db_path}")
    
    # Create engine
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        try:
            # Check if columns already exist
            result = conn.execute(text("PRAGMA table_info(search_requests)"))
            columns = [row[1] for row in result]
            
            if 'query_version' in columns:
                print("⚠️  Columns already exist. Skipping migration.")
                return
            
            print("📝 Adding query_version column...")
            conn.execute(text("""
                ALTER TABLE search_requests 
                ADD COLUMN query_version INTEGER NOT NULL DEFAULT 0
            """))
            
            print("📝 Adding query_history column...")
            conn.execute(text("""
                ALTER TABLE search_requests 
                ADD COLUMN query_history TEXT
            """))
            
            print("📝 Adding optimization_enabled column...")
            conn.execute(text("""
                ALTER TABLE search_requests 
                ADD COLUMN optimization_enabled BOOLEAN NOT NULL DEFAULT 1
            """))
            
            # Commit the changes
            conn.commit()
            
            print("✅ Migration completed successfully!")
            print("\nNew columns added:")
            print("  - query_version (INTEGER, default: 0)")
            print("  - query_history (TEXT/JSON)")
            print("  - optimization_enabled (BOOLEAN, default: TRUE)")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            raise


def downgrade():
    """Rollback the migration."""
    print("🔄 Rolling back migration: Remove query optimization fields...")
    
    # Note: SQLite doesn't support DROP COLUMN directly
    # You would need to recreate the table without these columns
    print("⚠️  SQLite doesn't support DROP COLUMN.")
    print("To rollback, you need to:")
    print("1. Create a new table without these columns")
    print("2. Copy data from old table")
    print("3. Drop old table")
    print("4. Rename new table")
    print("\nOr simply restore from a backup.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration for query optimization fields")
    parser.add_argument(
        "--downgrade",
        action="store_true",
        help="Rollback the migration"
    )
    
    args = parser.parse_args()
    
    if args.downgrade:
        downgrade()
    else:
        upgrade()

# Made with Bob
