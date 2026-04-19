"""
Database connection and session management.

This module provides:
- SQLAlchemy engine configuration
- Session factory for database operations
- Base class for all models
- Dependency injection for FastAPI routes
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# Database Engine
# ============================================================================

# Create SQLAlchemy engine
# The engine manages connections to the database
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.database_echo,  # Log SQL queries if enabled in config
    pool_pre_ping=True,  # Verify connections before using them
)

# ============================================================================
# Session Factory
# ============================================================================

# Create a SessionLocal class
# Each instance of SessionLocal will be a database session
SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-commit transactions
    autoflush=False,   # Don't auto-flush changes
    bind=engine        # Bind to our engine
)

# ============================================================================
# Base Class for Models
# ============================================================================

# Create a Base class for declarative models
# All database models will inherit from this Base class
Base = declarative_base()

# ============================================================================
# Database Dependency for FastAPI
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI routes.
    
    This function creates a new database session for each request
    and ensures it's properly closed after the request is complete.
    
    Usage in FastAPI routes:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    
    Yields:
        Session: SQLAlchemy database session
    
    Example:
        ```python
        from fastapi import Depends
        from sqlalchemy.orm import Session
        from app.database import get_db
        
        @app.get("/users")
        def read_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# Helper Functions
# ============================================================================

def init_db():
    """
    Initialize the database by creating all tables.
    
    This function should be called when the application starts
    to ensure all tables exist in the database.
    
    Note: This uses Base.metadata.create_all() which only creates
    tables that don't exist. It won't modify existing tables.
    For schema migrations, use Alembic instead.
    
    Example:
        ```python
        from app.database import init_db
        
        # In your main.py startup event
        @app.on_event("startup")
        async def startup_event():
            init_db()
        ```
    """
    Base.metadata.create_all(bind=engine)

def drop_db():
    """
    Drop all database tables.
    
    ⚠️  WARNING: This will delete all data in the database!
    Only use this in development or testing environments.
    
    Example:
        ```python
        from app.database import drop_db
        
        # Only in tests or development
        if settings.environment == "development":
            drop_db()
        ```
    """
    Base.metadata.drop_all(bind=engine)

def get_db_context():
    """
    Get a database session context manager.
    
    Use this when you need a database session outside of FastAPI routes.
    
    Returns:
        Session: Database session context manager
    
    Example:
        ```python
        from app.database import get_db_context
        
        with get_db_context() as db:
            user = db.query(User).first()
            print(user.name)
        # Session is automatically closed
        ```
    """
    return SessionLocal()

# ============================================================================
# Database Health Check
# ============================================================================

def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    
    Example:
        ```python
        from app.database import check_db_connection
        
        if check_db_connection():
            print("Database is connected!")
        else:
            print("Database connection failed!")
        ```
    """
    try:
        from sqlalchemy import text
        db = SessionLocal()
        # Try to execute a simple query
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

# ============================================================================
# Module Information
# ============================================================================

__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "init_db",
    "drop_db",
    "get_db_context",
    "check_db_connection",
]

# Made with Bob
