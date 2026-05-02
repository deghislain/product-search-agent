

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from app.config import settings


def upgrade():
    """Apply the migration."""
    
    # Use the backend database explicitly
    backend_db_path = os.path.join(os.path.dirname(__file__), '..', 'product_search.db')
    database_url = f"sqlite:///{backend_db_path}"
    
    print(f"📍 Using database: {backend_db_path}")
    
    # Create engine
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        try:   
            print("📝 Adding optimization_enabled column...")
            conn.execute(text("""
                ALTER TABLE search_requests 
                ADD COLUMN optimization_enabled BOOLEAN NOT NULL DEFAULT 1
            """))
            
            # Commit the changes
            conn.commit()
            
            print("✅ Table created successfully")
           
        except Exception as e:
            print(f"❌ Table creation failed: {e}")
            conn.rollback()
            raise


def downgrade():
    """Rollback the table creation."""
    print("🔄 Rolling back table creation: Remove created table...")
    
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
    
    parser = argparse.ArgumentParser(description="Database new table creation")
    parser.add_argument(
        "--downgrade",
        action="store_true",
        help="Rollback the table creation"
    )
    
    args = parser.parse_args()
    
    if args.downgrade:
        downgrade()
    else:
        upgrade()

# Made with Bob
