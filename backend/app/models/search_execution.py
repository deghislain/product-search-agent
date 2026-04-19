"""
SearchExecution model for tracking individual search runs.

This model represents a single execution of a search request,
tracking when it started, completed, and what results were found.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.models import ExecutionStatus


class SearchExecution(Base):
    """
    SearchExecution model for tracking each search run.
    
    A SearchExecution represents a single automated run of a SearchRequest.
    The system creates a new execution every time it searches for products
    (typically every 2 hours). This allows tracking of search history,
    performance metrics, and debugging.
    
    Attributes:
        id (str): Unique identifier (UUID)
        search_request_id (str): Foreign key to parent SearchRequest
        started_at (datetime): When the execution started
        completed_at (datetime, optional): When the execution finished
        status (str): Current status (pending, running, completed, failed, cancelled)
        products_found (int): Total number of products found
        matches_found (int): Number of products that met match criteria
        error_message (str, optional): Error details if execution failed
        
    Relationships:
        search_request: Parent SearchRequest that triggered this execution
        products: List of Product records found in this execution
    
    Example:
        ```python
        from app.models import SearchExecution, ExecutionStatus
        from app.database import SessionLocal
        from datetime import datetime
        
        # Create a new execution
        execution = SearchExecution(
            search_request_id=search.id,
            started_at=datetime.utcnow(),
            status=ExecutionStatus.RUNNING
        )
        
        # Save to database
        db = SessionLocal()
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        print(f"Execution started: {execution.id}")
        
        # Update after search completes
        execution.complete(products_found=25, matches_found=3)
        db.commit()
        
        # Check if successful
        if execution.is_successful():
            print(f"Found {execution.matches_found} matches!")
        
        # Handle errors
        try:
            # ... search logic ...
            pass
        except Exception as e:
            execution.fail(str(e))
            db.commit()
        
        db.close()
        ```
    """
    
    __tablename__ = "search_executions"
    
    # ========================================================================
    # Primary Key
    # ========================================================================
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique identifier for the search execution"
    )
    
    # ========================================================================
    # Foreign Keys
    # ========================================================================
    
    search_request_id = Column(
        String(36),
        ForeignKey('search_requests.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID of the parent search request"
    )
    
    # ========================================================================
    # Execution Timing
    # ========================================================================
    
    started_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When the search execution started"
    )
    
    completed_at = Column(
        DateTime,
        nullable=True,
        comment="When the search execution completed (null if still running)"
    )
    
    # ========================================================================
    # Execution Status
    # ========================================================================
    
    status = Column(
        String(20),
        nullable=False,
        default=ExecutionStatus.RUNNING.value,
        index=True,
        comment="Current status of the execution (pending, running, completed, failed, cancelled)"
    )
    
    # ========================================================================
    # Execution Metrics
    # ========================================================================
    
    products_found = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of products found during this execution"
    )
    
    matches_found = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of products that met the match criteria"
    )
    
    # ========================================================================
    # Error Handling
    # ========================================================================
    
    error_message = Column(
        Text,
        nullable=True,
        comment="Error message if the execution failed"
    )
    
    # ========================================================================
    # Relationships
    # ========================================================================
    
    # Many-to-one: Multiple executions belong to one search request
    # NOTE: This will be uncommented after SearchRequest model is updated
    # search_request = relationship(
    #     "SearchRequest",
    #     back_populates="executions"
    # )
    
    # One-to-many: An execution can find multiple products
    # NOTE: This will be uncommented after Product model is created
    # products = relationship(
    #     "Product",
    #     back_populates="search_execution",
    #     cascade="all, delete-orphan",
    #     lazy="dynamic"
    # )
    
    # ========================================================================
    # Indexes for Performance
    # ========================================================================
    
    __table_args__ = (
        # Composite index for querying executions by search and status
        Index('idx_execution_search_status', 'search_request_id', 'status'),
        # Index for querying recent executions
        Index('idx_execution_started', 'started_at'),
    )
    
    # ========================================================================
    # Methods
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of SearchExecution."""
        return (
            f"<SearchExecution(id={self.id}, "
            f"search_request_id={self.search_request_id}, "
            f"status={self.status}, "
            f"matches={self.matches_found})>"
        )
    
    def complete(self, products_found: int = 0, matches_found: int = 0) -> None:
        """
        Mark the execution as completed successfully.
        
        Args:
            products_found: Total number of products found
            matches_found: Number of products that met match criteria
        
        Example:
            ```python
            execution.complete(products_found=25, matches_found=3)
            db.commit()
            ```
        """
        self.status = ExecutionStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        self.products_found = products_found
        self.matches_found = matches_found
        self.error_message = None
    
    def fail(self, error_message: str) -> None:
        """
        Mark the execution as failed with an error message.
        
        Args:
            error_message: Description of what went wrong
        
        Example:
            ```python
            try:
                # ... search logic ...
                pass
            except Exception as e:
                execution.fail(str(e))
                db.commit()
            ```
        """
        self.status = ExecutionStatus.FAILED.value
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
    
    def cancel(self) -> None:
        """
        Mark the execution as cancelled.
        
        Example:
            ```python
            execution.cancel()
            db.commit()
            ```
        """
        self.status = ExecutionStatus.CANCELLED.value
        self.completed_at = datetime.utcnow()
    
    def is_running(self) -> bool:
        """
        Check if the execution is currently running.
        
        Returns:
            bool: True if status is RUNNING, False otherwise
        
        Example:
            ```python
            if execution.is_running():
                print("Search is in progress...")
            ```
        """
        return self.status == ExecutionStatus.RUNNING.value
    
    def is_completed(self) -> bool:
        """
        Check if the execution completed successfully.
        
        Returns:
            bool: True if status is COMPLETED, False otherwise
        
        Example:
            ```python
            if execution.is_completed():
                print(f"Found {execution.matches_found} matches")
            ```
        """
        return self.status == ExecutionStatus.COMPLETED.value
    
    def is_failed(self) -> bool:
        """
        Check if the execution failed.
        
        Returns:
            bool: True if status is FAILED, False otherwise
        
        Example:
            ```python
            if execution.is_failed():
                print(f"Error: {execution.error_message}")
            ```
        """
        return self.status == ExecutionStatus.FAILED.value
    
    def is_successful(self) -> bool:
        """
        Check if the execution completed successfully.
        
        Alias for is_completed() for better readability.
        
        Returns:
            bool: True if execution completed without errors
        
        Example:
            ```python
            if execution.is_successful():
                print("Search completed successfully!")
            ```
        """
        return self.is_completed()
    
    def duration_seconds(self) -> float:
        """
        Calculate the duration of the execution in seconds.
        
        Returns:
            float: Duration in seconds, or 0 if not completed
        
        Example:
            ```python
            duration = execution.duration_seconds()
            print(f"Search took {duration:.2f} seconds")
            ```
        """
        if self.completed_at is None:
            return 0.0
        delta = self.completed_at - self.started_at
        return delta.total_seconds()
    
    def has_matches(self) -> bool:
        """
        Check if any matches were found.
        
        Returns:
            bool: True if matches_found > 0
        
        Example:
            ```python
            if execution.has_matches():
                print("Found matching products!")
            ```
        """
        return self.matches_found > 0
    
    def match_rate(self) -> float:
        """
        Calculate the percentage of products that were matches.
        
        Returns:
            float: Match rate as percentage (0-100), or 0 if no products found
        
        Example:
            ```python
            rate = execution.match_rate()
            print(f"Match rate: {rate:.1f}%")
            ```
        """
        if self.products_found == 0:
            return 0.0
        return (self.matches_found / self.products_found) * 100
    
    def to_dict(self) -> dict:
        """
        Convert the execution to a dictionary.
        
        Returns:
            dict: Dictionary representation of the execution
        
        Example:
            ```python
            execution_dict = execution.to_dict()
            print(execution_dict['status'])
            ```
        """
        return {
            'id': self.id,
            'search_request_id': self.search_request_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'products_found': self.products_found,
            'matches_found': self.matches_found,
            'error_message': self.error_message,
            'duration_seconds': self.duration_seconds(),
            'match_rate': self.match_rate(),
        }

# Made with Bob