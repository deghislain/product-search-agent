"""
Database models package.

This module exports all database models and enums used throughout the application.
All models inherit from the Base class defined in app.database.

Quick Start:
    ```python
    from app.models import SearchRequest, Product, SearchStatus
    from app.database import SessionLocal
    
    # Create a search request
    search = SearchRequest(
        product_name="iPhone 13",
        product_description="Looking for iPhone 13",
        budget=600.0,
        status=SearchStatus.ACTIVE
    )
    
    # Save to database
    db = SessionLocal()
    db.add(search)
    db.commit()
    db.close()
    ```

Available Models:
    - SearchRequest: User search criteria and preferences
    - SearchExecution: Individual search run tracking
    - Product: Scraped product information
    - Notification: User notifications and alerts

Available Enums:
    - SearchStatus: Status of search requests (ACTIVE, PAUSED, COMPLETED, CANCELLED)
    - ExecutionStatus: Status of search executions (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED)
    - NotificationType: Types of notifications (MATCH_FOUND, SEARCH_STARTED, SEARCH_COMPLETED, ERROR_OCCURRED)

Database Base:
    - Base: SQLAlchemy declarative base class for all models
"""

from enum import Enum

# ============================================================================
# Enums
# ============================================================================

class SearchStatus(str, Enum):
    """
    Status of a search request.
    
    Attributes:
        ACTIVE: Search is active and will run on schedule
        PAUSED: Search is temporarily paused by user
        COMPLETED: Search has been completed/finished
        CANCELLED: Search was cancelled by user
    
    Example:
        ```python
        from app.models import SearchStatus
        
        # Create a new search with active status
        search = SearchRequest(
            product_name="iPhone 13",
            status=SearchStatus.ACTIVE
        )
        
        # Pause the search
        search.status = SearchStatus.PAUSED
        
        # Check status
        if search.status == SearchStatus.ACTIVE:
            print("Search is running")
        ```
    """
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class NotificationType(str, Enum):
    """
    Type of notification sent to user.
    
    Attributes:
        MATCH_FOUND: A product matching criteria was found
        SEARCH_STARTED: A search execution has started
        SEARCH_COMPLETED: A search execution has completed
        ERROR_OCCURRED: An error occurred during search
    
    Example:
        ```python
        from app.models import NotificationType
        
        # Create a match notification
        notification = Notification(
            type=NotificationType.MATCH_FOUND,
            message="Found iPhone 13 for $450!"
        )
        
        # Create an error notification
        error_notification = Notification(
            type=NotificationType.ERROR_OCCURRED,
            message="Craigslist scraper failed"
        )
        ```
    """
    MATCH_FOUND = "match_found"
    SEARCH_STARTED = "search_started"
    SEARCH_COMPLETED = "search_completed"
    ERROR_OCCURRED = "error_occurred"


class ExecutionStatus(str, Enum):
    """
    Status of a search execution.
    
    Attributes:
        PENDING: Execution is queued but not started
        RUNNING: Execution is currently in progress
        COMPLETED: Execution finished successfully
        FAILED: Execution failed with errors
        CANCELLED: Execution was cancelled
    
    Example:
        ```python
        from app.models import ExecutionStatus
        
        # Start a new execution
        execution = SearchExecution(
            search_request_id=search_id,
            status=ExecutionStatus.RUNNING
        )
        
        # Mark as completed
        execution.status = ExecutionStatus.COMPLETED
        execution.completed_at = datetime.utcnow()
        ```
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# Import Base from database module
# ============================================================================

from app.database import Base

# ============================================================================
# Model imports (will be added as we create them)
# ============================================================================

# Import models as they are created
from app.models.search_request import SearchRequest
from app.models.search_execution import SearchExecution
from app.models.product import Product
from app.models.notification import Notification
from app.models.email_preference import EmailPreference
from app.models.user_interaction import UserInteraction
from app.models.user_preference import UserPreference   
# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # Enums
    "SearchStatus",
    "NotificationType",
    "ExecutionStatus",
    # Base class
    "Base",
    # Models
    "SearchRequest",
    "SearchExecution",
    "Product",
    "Notification",
    "EmailPreference", 
    "UserInteraction",
    "UserPreference",
    # Utility functions
    "get_all_models",
    "get_all_enums",
    "get_model_names",
]


# ============================================================================
# Utility Functions
# ============================================================================

def get_all_models() -> list:
    """
    Get a list of all model classes.
    
    Returns:
        list: List of model classes [SearchRequest, SearchExecution, Product, Notification,UserInteraction,UserPreference]
    
    Example:
        ```python
        from app.models import get_all_models
        
        models = get_all_models()
        for model in models:
            print(f"Model: {model.__name__}")
            print(f"Table: {model.__tablename__}")
        ```
    """
    return [SearchRequest, SearchExecution, Product, Notification, EmailPreference, UserInteraction, UserPreference]


def get_all_enums() -> dict:
    """
    Get a dictionary of all enum classes.
    
    Returns:
        dict: Dictionary mapping enum names to enum classes
    
    Example:
        ```python
        from app.models import get_all_enums
        
        enums = get_all_enums()
        for name, enum_class in enums.items():
            print(f"{name}: {[e.value for e in enum_class]}")
        ```
    """
    return {
        "SearchStatus": SearchStatus,
        "NotificationType": NotificationType,
        "ExecutionStatus": ExecutionStatus,
    }


def get_model_names() -> list:
    """
    Get a list of all model table names.
    
    Returns:
        list: List of table names
    
    Example:
        ```python
        from app.models import get_model_names
        
        tables = get_model_names()
        print(f"Tables: {tables}")
        # Output: ['search_requests', 'search_executions', 'products', 'notifications']
        ```
    """
    return [model.__tablename__ for model in get_all_models()]


# Made with Bob
