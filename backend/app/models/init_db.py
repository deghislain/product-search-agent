"""
Database initialization script.

This script provides functions to initialize, reset, and manage the database.
It creates all tables defined in the models and provides utilities for
database management during development and production.
"""

import sys
from pathlib import Path
from sqlalchemy import inspect, text

# Add backend directory to path for standalone execution
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import Base, engine, SessionLocal, check_db_connection
from app.models.search_request import SearchRequest
from app.models.search_execution import SearchExecution
from app.models.product import Product
from app.models.notification import Notification
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def init_db(verbose: bool = True) -> bool:
    """
    Initialize the database by creating all tables.
    
    This function creates all tables defined in the models if they don't
    already exist. It's safe to run multiple times as it won't modify
    existing tables.
    
    Args:
        verbose: Whether to print status messages (default: True)
    
    Returns:
        bool: True if successful, False otherwise
    
    Example:
        ```python
        from app.models.init_db import init_db
        
        # Initialize database
        if init_db():
            print("Database ready!")
        ```
    """
    try:
        if verbose:
            logger.info("="*70)
            logger.info("DATABASE INITIALIZATION")
            logger.info("="*70)
            logger.info("\nCreating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        if verbose:
            # Verify tables were created
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            logger.debug(f"\n✅ Successfully created {len(tables)} tables:")
            for table in sorted(tables):
                logger.debug(f"   - {table}")
            
            logger.info("\n" + "="*70)
            logger.info("DATABASE INITIALIZATION COMPLETE")
            logger.info("="*70)
        
        return True
        
    except Exception as e:
        if verbose:
            logger.error(f"\n❌ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
        return False


def drop_db(verbose: bool = True, confirm: bool = True) -> bool:
    """
    Drop all database tables.
    
    ⚠️  WARNING: This will delete ALL data in the database!
    Only use this in development or testing environments.
    
    Args:
        verbose: Whether to print status messages (default: True)
        confirm: Whether to require confirmation (default: True)
    
    Returns:
        bool: True if successful, False otherwise
    
    Example:
        ```python
        from app.models.init_db import drop_db
        
        # Drop all tables (will ask for confirmation)
        drop_db()
        
        # Drop without confirmation (dangerous!)
        drop_db(confirm=False)
        ```
    """
    try:
        if confirm:
            if verbose:
                logger.debug("\n⚠️  WARNING: This will delete ALL data in the database!")
                response = input("Are you sure you want to continue? (yes/no): ")
                if response.lower() != 'yes':
                    logger.debug("Operation cancelled.")
                    return False
        
        if verbose:
            logger.debug("\n" + "="*70)
            logger.debug("DROPPING DATABASE TABLES")
            logger.debug("="*70)
            logger.debug("\nDropping all tables...")
        
        # Get table names before dropping
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        
        if verbose:
            logger.debug(f"\n✅ Successfully dropped {len(tables)} tables:")
            for table in sorted(tables):
                logger.debug(f"   - {table}")
            
            logger.debug("\n" + "="*70)
            logger.debug("DATABASE TABLES DROPPED")
            logger.debug("="*70)
        
        return True
        
    except Exception as e:
        if verbose:
            logger.error(f"\n❌ Error dropping database: {e}")
            import traceback
            traceback.print_exc()
        return False


def reset_db(verbose: bool = True, confirm: bool = True) -> bool:
    """
    Reset the database by dropping and recreating all tables.
    
    ⚠️  WARNING: This will delete ALL data in the database!
    
    Args:
        verbose: Whether to print status messages (default: True)
        confirm: Whether to require confirmation (default: True)
    
    Returns:
        bool: True if successful, False otherwise
    
    Example:
        ```python
        from app.models.init_db import reset_db
        
        # Reset database (will ask for confirmation)
        reset_db()
        ```
    """
    if verbose:
        logger.debug("\n" + "="*70)
        logger.debug("DATABASE RESET")
        logger.debug("="*70)
    
    # Drop existing tables
    if not drop_db(verbose=verbose, confirm=confirm):
        return False
    
    # Create new tables
    if not init_db(verbose=verbose):
        return False
    
    if verbose:
        logger.debug("\n✅ Database reset complete!")
    
    return True


def verify_db(verbose: bool = True) -> bool:
    """
    Verify database connection and table structure.
    
    Args:
        verbose: Whether to print detailed information (default: True)
    
    Returns:
        bool: True if database is properly configured, False otherwise
    
    Example:
        ```python
        from app.models.init_db import verify_db
        
        if verify_db():
            logger.debug("Database is ready!")
        ```
    """
    try:
        if verbose:
            logger.debug("\n" + "="*70)
            logger.debug("DATABASE VERIFICATION")
            logger.debug("="*70)
        
        # Check connection
        if not check_db_connection():
            if verbose:
                logger.debug("\n❌ Database connection failed!")
            return False
        
        if verbose:
            logger.debug("\n✅ Database connection successful")
        
        # Check tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['search_requests', 'search_executions', 'products', 'notifications']
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            if verbose:
                logger.debug(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
                logger.debug("Run init_db() to create missing tables.")
            return False
        
        if verbose:
            logger.debug(f"\n✅ All {len(expected_tables)} required tables exist:")
            for table in sorted(expected_tables):
                logger.debug(f"   - {table}")
            
            # Show table details
            logger.debug("\n📋 Table Details:")
            for table in sorted(expected_tables):
                columns = inspector.get_columns(table)
                indexes = inspector.get_indexes(table)
                fks = inspector.get_foreign_keys(table)
                
                logger.debug(f"\n   {table}:")
                logger.debug(f"      Columns: {len(columns)}")
                logger.debug(f"      Indexes: {len(indexes)}")
                logger.debug(f"      Foreign Keys: {len(fks)}")
        
        if verbose:
            logger.debug("\n" + "="*70)
            logger.debug("DATABASE VERIFICATION COMPLETE")
            logger.debug("="*70)
        
        return True
        
    except Exception as e:
        if verbose:
            logger.debug(f"\n❌ Error verifying database: {e}")
            import traceback
            traceback.print_exc()
        return False


def get_db_stats(verbose: bool = True) -> dict:
    """
    Get statistics about the database.
    
    Args:
        verbose: Whether to print statistics (default: True)
    
    Returns:
        dict: Dictionary containing database statistics
    
    Example:
        ```python
        from app.models.init_db import get_db_stats
        
        stats = get_db_stats()
        print(f"Total searches: {stats['search_requests']}")
        ```
    """
    try:
        db = SessionLocal()
        
        stats = {
            'search_requests': db.query(SearchRequest).count(),
            'search_executions': db.query(SearchExecution).count(),
            'products': db.query(Product).count(),
            'notifications': db.query(Notification).count(),
        }
        
        if verbose:
            logger.debug("\n" + "="*70)
            logger.debug("DATABASE STATISTICS")
            logger.debug("="*70)
            logger.debug(f"\n📊 Record Counts:")
            logger.debug(f"   Search Requests: {stats['search_requests']}")
            logger.debug(f"   Search Executions: {stats['search_executions']}")
            logger.debug(f"   Products: {stats['products']}")
            logger.debug(f"   Notifications: {stats['notifications']}")
            logger.debug(f"\n   Total Records: {sum(stats.values())}")
            logger.debug("\n" + "="*70)
        
        db.close()
        return stats
        
    except Exception as e:
        if verbose:
            logger.debug(f"\n❌ Error getting database stats: {e}")
        return {}


def main():
    """Main function for command-line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Database initialization and management script'
    )
    parser.add_argument(
        'action',
        choices=['init', 'drop', 'reset', 'verify', 'stats'],
        help='Action to perform'
    )
    parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='Skip confirmation prompts (dangerous!)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress output messages'
    )
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    confirm = not args.no_confirm
    
    if args.action == 'init':
        success = init_db(verbose=verbose)
    elif args.action == 'drop':
        success = drop_db(verbose=verbose, confirm=confirm)
    elif args.action == 'reset':
        success = reset_db(verbose=verbose, confirm=confirm)
    elif args.action == 'verify':
        success = verify_db(verbose=verbose)
    elif args.action == 'stats':
        stats = get_db_stats(verbose=verbose)
        success = bool(stats)
    else:
        logger.debug(f"Unknown action: {args.action}")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    # If run without arguments, just initialize the database
    if len(sys.argv) == 1:
        logger.info("\nDatabase Initialization Script")
        logger.info("Usage: python -m app.models.init_db [action]")
        logger.info("\nActions:")
        logger.info("  init   - Create all database tables")
        logger.info("  drop   - Drop all database tables")
        logger.info("  reset  - Drop and recreate all tables")
        logger.info("  verify - Verify database structure")
        logger.info("  stats  - Show database statistics")
        logger.info("\nRunning default action: init\n")
        init_db()
    else:
        main()

# Made with Bob