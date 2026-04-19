"""
FastAPI dependencies for database sessions and other shared resources.

This module provides dependency functions that can be injected into
FastAPI route handlers using the Depends() function.

Dependencies include:
- Database session management
- Authentication (future)
- Rate limiting (future)
"""

from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that provides a database session to route handlers.
    
    This function creates a new SQLAlchemy session for each request and
    ensures it's properly closed after the request is complete, even if
    an error occurs.
    
    The session is yielded (not returned) so FastAPI can manage its lifecycle:
    1. Session is created before the route handler runs
    2. Session is passed to the route handler
    3. Session is closed after the route handler completes
    
    Yields:
        Session: SQLAlchemy database session
        
    Example Usage:
        ```python
        from fastapi import APIRouter, Depends
        from sqlalchemy.orm import Session
        from app.api.dependencies import get_db
        from app.models import SearchRequest
        
        router = APIRouter()
        
        @router.get("/search-requests")
        def list_searches(db: Session = Depends(get_db)):
            # db is automatically provided and will be closed after
            searches = db.query(SearchRequest).all()
            return searches
        ```
    
    Notes:
        - Each request gets its own database session
        - Sessions are automatically closed, preventing connection leaks
        - If an exception occurs, the session is still properly closed
        - This follows the "dependency injection" pattern
    """
    # Create a new database session
    db = SessionLocal()
    
    try:
        # Yield the session to the route handler
        # The route handler will use this session for database operations
        yield db
    finally:
        # This runs after the route handler completes (or if an error occurs)
        # Ensures the session is always closed, preventing connection leaks
        db.close()


# Future dependencies can be added here, for example:

# def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
#     """Get the currently authenticated user."""
#     # Verify token and return user
#     pass

# def rate_limit(request: Request) -> None:
#     """Rate limiting dependency."""
#     # Check rate limits
#     pass

# Made with Bob
