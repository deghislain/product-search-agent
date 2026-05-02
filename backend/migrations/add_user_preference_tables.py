"""
Database Migration: Add User Preference Learning Tables

This migration adds the user_interactions and user_preferences tables
required for Phase 1.3 User Preference Learning feature.

Usage:
    python backend/migrations/add_user_preference_tables.py
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import inspect, text
from app.database import engine, SessionLocal
from app.models.user_interaction import UserInteraction
from app.models.user_preference import UserPreference
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def migrate_up():
    """
    Apply the migration - create new tables.
    """
    logger.info("="*70)
    logger.info("MIGRATION: Add User Preference Learning Tables")
    logger.info("="*70)
    
    # Check if tables already exist
    user_interactions_exists = check_table_exists('user_interactions')
    user_preferences_exists = check_table_exists('user_preferences')
    
    if user_interactions_exists and user_preferences_exists:
        logger.info("✅ Tables already exist. No migration needed.")
        return True
    
    try:
        # Create tables
        logger.info("\n📝 Creating tables...")
        
        if not user_interactions_exists:
            UserInteraction.__table__.create(engine)
            logger.info("✅ Created table: user_interactions")
        else:
            logger.info("⏭️  Table already exists: user_interactions")
        
        if not user_preferences_exists:
            UserPreference.__table__.create(engine)
            logger.info("✅ Created table: user_preferences")
        else:
            logger.info("⏭️  Table already exists: user_preferences")
        
        # Verify tables were created
        logger.info("\n🔍 Verifying tables...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'user_interactions' in tables and 'user_preferences' in tables:
            logger.info("✅ Migration successful!")
            logger.info("\n📊 Table Details:")
            
            # Show user_interactions columns
            ui_columns = inspector.get_columns('user_interactions')
            logger.info(f"\n  user_interactions ({len(ui_columns)} columns):")
            for col in ui_columns:
                logger.info(f"    - {col['name']}: {col['type']}")
            
            # Show user_preferences columns
            up_columns = inspector.get_columns('user_preferences')
            logger.info(f"\n  user_preferences ({len(up_columns)} columns):")
            for col in up_columns:
                logger.info(f"    - {col['name']}: {col['type']}")
            
            logger.info("\n" + "="*70)
            logger.info("MIGRATION COMPLETE")
            logger.info("="*70)
            return True
        else:
            logger.error("❌ Migration failed - tables not found after creation")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def migrate_down():
    """
    Rollback the migration - drop tables.
    
    ⚠️  WARNING: This will delete all user interaction and preference data!
    """
    logger.info("="*70)
    logger.info("ROLLBACK: Remove User Preference Learning Tables")
    logger.info("="*70)
    logger.warning("\n⚠️  WARNING: This will delete all user interaction and preference data!")
    
    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        logger.info("Rollback cancelled.")
        return False
    
    try:
        logger.info("\n📝 Dropping tables...")
        
        # Drop tables in reverse order (to handle foreign keys)
        if check_table_exists('user_preferences'):
            UserPreference.__table__.drop(engine)
            logger.info("✅ Dropped table: user_preferences")
        
        if check_table_exists('user_interactions'):
            UserInteraction.__table__.drop(engine)
            logger.info("✅ Dropped table: user_interactions")
        
        logger.info("\n" + "="*70)
        logger.info("ROLLBACK COMPLETE")
        logger.info("="*70)
        return True
        
    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function for command-line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Database migration for user preference learning tables'
    )
    parser.add_argument(
        'action',
        choices=['up', 'down', 'status'],
        help='Migration action: up (apply), down (rollback), or status (check)'
    )
    
    args = parser.parse_args()
    
    if args.action == 'up':
        success = migrate_up()
    elif args.action == 'down':
        success = migrate_down()
    elif args.action == 'status':
        logger.info("="*70)
        logger.info("MIGRATION STATUS")
        logger.info("="*70)
        
        ui_exists = check_table_exists('user_interactions')
        up_exists = check_table_exists('user_preferences')
        
        logger.info(f"\nuser_interactions: {'✅ EXISTS' if ui_exists else '❌ NOT FOUND'}")
        logger.info(f"user_preferences: {'✅ EXISTS' if up_exists else '❌ NOT FOUND'}")
        
        if ui_exists and up_exists:
            logger.info("\n✅ Migration has been applied")
            
            # Show record counts
            db = SessionLocal()
            ui_count = db.query(UserInteraction).count()
            up_count = db.query(UserPreference).count()
            db.close()
            
            logger.info(f"\n📊 Record Counts:")
            logger.info(f"  User Interactions: {ui_count}")
            logger.info(f"  User Preferences: {up_count}")
        else:
            logger.info("\n❌ Migration has not been applied")
        
        logger.info("\n" + "="*70)
        success = True
    else:
        logger.error(f"Unknown action: {args.action}")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, show usage
        print("\nDatabase Migration: User Preference Learning Tables")
        print("\nUsage: python backend/migrations/add_user_preference_tables.py [action]")
        print("\nActions:")
        print("  up     - Apply migration (create tables)")
        print("  down   - Rollback migration (drop tables)")
        print("  status - Check migration status")
        print("\nExample:")
        print("  python backend/migrations/add_user_preference_tables.py up")
        sys.exit(0)
    else:
        main()


# Made with Bob