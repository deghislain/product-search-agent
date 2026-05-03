"""
SearchRequest model for storing user search criteria.

This model represents a user's search request with product criteria,
budget constraints, and matching preferences.
"""

from sqlalchemy import Column, String, Float, DateTime, Boolean, Text, Enum as SQLEnum, Index, Integer, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.models import SearchStatus


class SearchRequest(Base):
    """
    SearchRequest model for storing product search criteria.
    
    A SearchRequest represents a user's desire to find a specific product
    within a budget. The system will automatically search for matching
    products every 2 hours (configurable) until the search is paused or cancelled.
    
    Attributes:
        id (str): Unique identifier (UUID)
        product_name (str): Name/title of the product to search for
        product_description (str): Detailed description of desired product
        budget (float): Maximum price willing to pay
        location (str, optional): Geographic location for search
        match_threshold (float): Minimum similarity score (0-100) for matches
        status (SearchStatus): Current status of the search
        created_at (datetime): When the search was created
        updated_at (datetime): When the search was last modified
        
    Relationships:
        executions: List of SearchExecution records for this search
        notifications: List of Notification records for this search
    
    Example:
        ```python
        from app.models import SearchRequest, SearchStatus
        from app.database import SessionLocal
        
        # Create a new search request
        search = SearchRequest(
            product_name="iPhone 13",
            product_description="Looking for iPhone 13 in good condition, 128GB or more",
            budget=600.0,
            location="Boston, MA",
            match_threshold=75.0,
            status=SearchStatus.ACTIVE
        )
        
        # Save to database
        db = SessionLocal()
        db.add(search)
        db.commit()
        db.refresh(search)
        
        print(f"Created search: {search.id}")
        print(f"Status: {search.status}")
        
        # Update search
        search.budget = 650.0
        search.updated_at = datetime.utcnow()
        db.commit()
        
        # Pause search
        search.status = SearchStatus.PAUSED
        db.commit()
        
        db.close()
        ```
    """
    
    __tablename__ = "search_requests"
    
    # ========================================================================
    # Primary Key
    # ========================================================================
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique identifier for the search request"
    )
    
    # ========================================================================
    # Product Information
    # ========================================================================
    
    product_name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Name or title of the product to search for"
    )
    
    product_description = Column(
        Text,
        nullable=False,
        comment="Detailed description of the desired product"
    )
    
    # ========================================================================
    # Search Constraints
    # ========================================================================
    
    budget = Column(
        Float,
        nullable=False,
        index=True,
        comment="Maximum price willing to pay"
    )
    
    location = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Geographic location for search (e.g., 'Boston, MA')"
    )
    
    # ========================================================================
    # Matching Configuration
    # ========================================================================
    
    match_threshold = Column(
        Float,
        nullable=False,
        default=70.0,
        comment="Minimum similarity score (0-100) for a product to be considered a match"
    )
    
    # ========================================================================
    # Status and Timestamps
    # ========================================================================
    
    status = Column(
        SQLEnum(SearchStatus),
        nullable=False,
        default=SearchStatus.ACTIVE,
        index=True,
        comment="Current status of the search request"
    )
    
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="When the search request was created"
    )
    
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="When the search request was last updated"
    )
    
    # ========================================================================
    # Query Optimization Fields (Agentic Features)
    # ========================================================================
    
    query_version = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Track query iterations for optimization"
    )
    
    query_history = Column(
        JSON,
        nullable=True,
        default=list,
        comment="Store all query versions with timestamps and performance metrics"
    )
    
    optimization_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Enable/disable automatic query optimization"
    )
    
    # ========================================================================
    # Platform Selection
    # ========================================================================
    
    search_craigslist = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Enable the search on Craigslist"
    )
    search_ebay = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Enable the search on Ebay"
    )
    search_facebook = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Enable the search on Facebook Marketplace"
    )
    email_preferences = relationship(
    "EmailPreference",
    back_populates="search_request",
    cascade="all, delete-orphan"  # Delete preferences when search is deleted
)
    email_address = Column(String, nullable=True, index=True)
    # ========================================================================
    # Indexes for Performance
    # ========================================================================
    
    __table_args__ = (
        # Index for filtering active/paused searches
        Index('idx_search_requests_status', 'status'),
    )
    
    # ========================================================================
    # Relationships
    # ========================================================================
    
    # NOTE: Relationships will be uncommented after related models are created
    
    # One-to-many: A search request can have multiple executions
    # executions = relationship(
    #     "SearchExecution",
    #     back_populates="search_request",
    #     cascade="all, delete-orphan",
    #     lazy="dynamic"
    # )
    
    # One-to-many: A search request can have multiple notifications
    # notifications = relationship(
    #     "Notification",
    #     back_populates="search_request",
    #     cascade="all, delete-orphan",
    #     lazy="dynamic"
    # )
    
    # ========================================================================
    # Methods
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of SearchRequest."""
        return (
            f"<SearchRequest(id={self.id}, "
            f"product={self.product_name}, "
            f"budget=${self.budget:.2f}, "
            f"status={self.status.value})>"
        )
    
    def is_active(self) -> bool:
        """
        Check if the search is currently active.
        
        Returns:
            bool: True if status is ACTIVE, False otherwise
        
        Example:
            ```python
            if search.is_active():
                print("Search is running")
            ```
        """
        return self.status == SearchStatus.ACTIVE
    
    def pause(self) -> None:
        """
        Pause the search request.
        
        Sets status to PAUSED and updates the timestamp.
        Remember to commit the session after calling this method.
        
        Example:
            ```python
            search.pause()
            db.commit()
            ```
        """
        self.status = SearchStatus.PAUSED
        self.updated_at = datetime.utcnow()
    
    def resume(self) -> None:
        """
        Resume a paused search request.
        
        Sets status to ACTIVE and updates the timestamp.
        Remember to commit the session after calling this method.
        
        Example:
            ```python
            search.resume()
            db.commit()
            ```
        """
        self.status = SearchStatus.ACTIVE
        self.updated_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """
        Cancel the search request.
        
        Sets status to CANCELLED and updates the timestamp.
        Remember to commit the session after calling this method.
        
        Example:
            ```python
            search.cancel()
            db.commit()
            ```
        """
        self.status = SearchStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def complete(self) -> None:
        """
        Mark the search request as completed.
        
        Sets status to COMPLETED and updates the timestamp.
        Remember to commit the session after calling this method.
        
        Example:
            ```python
            search.complete()
            db.commit()
            ```
        """
        self.status = SearchStatus.COMPLETED
        self.updated_at = datetime.utcnow()
    
    def update_budget(self, new_budget: float) -> None:
        """
        Update the budget for this search.
        
        Args:
            new_budget: New maximum price
        
        Example:
            ```python
            search.update_budget(700.0)
            db.commit()
            ```
        """
        self.budget = new_budget
        self.updated_at = datetime.utcnow()
    
    def update_threshold(self, new_threshold: float) -> None:
        """
        Update the match threshold for this search.
        
        Args:
            new_threshold: New threshold value (0-100)
        
        Example:
            ```python
            search.update_threshold(80.0)
            db.commit()
            ```
        """
        if not 0 <= new_threshold <= 100:
            raise ValueError("Threshold must be between 0 and 100")
        self.match_threshold = new_threshold
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Convert the search request to a dictionary.
        
        Returns:
            dict: Dictionary representation of the search request
        
        Example:
            ```python
            search_dict = search.to_dict()
            print(search_dict['product_name'])
            ```
        """
        return {
            'id': self.id,
            'product_name': self.product_name,
            'product_description': self.product_description,
            'budget': self.budget,
            'location': self.location,
            'match_threshold': self.match_threshold,
            'status': self.status.value,
            'query_version': self.query_version,
            'query_history': self.query_history,
            'optimization_enabled': self.optimization_enabled,
            'search_craigslist': self.search_craigslist,
            'search_ebay': self.search_ebay,
            'search_facebook': self.search_facebook,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

# Made with Bob
