"""
Notification model for storing user notifications.

This model represents notifications sent to users about search events,
matches found, errors, and other important updates.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base
from app.models import NotificationType


class Notification(Base):
    """
    Notification model for storing user notifications.
    
    A Notification represents a message sent to the user about their search.
    Notifications can be triggered by various events such as finding a match,
    starting a search, completing a search, or encountering an error.
    
    Attributes:
        id (str): Unique identifier (UUID)
        search_request_id (str): Foreign key to parent SearchRequest
        product_id (str, optional): Foreign key to related Product (if applicable)
        type (NotificationType): Type of notification
        message (str): Notification message text
        read (bool): Whether notification has been read
        created_at (datetime): When the notification was created
        
    Relationships:
        search_request: Parent SearchRequest that triggered this notification
        product: Related Product (if notification is about a specific product)
    
    Example:
        ```python
        from app.models import Notification, NotificationType
        from app.database import SessionLocal
        
        # Create a match found notification
        notification = Notification(
            search_request_id=search.id,
            product_id=product.id,
            type=NotificationType.MATCH_FOUND,
            message=f"Found match: {product.title} for ${product.price}"
        )
        
        # Save to database
        db = SessionLocal()
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        print(f"Notification created: {notification.id}")
        print(f"Type: {notification.type.value}")
        print(f"Read: {notification.read}")
        
        # Mark as read
        notification.mark_as_read()
        db.commit()
        
        # Check if unread
        if notification.is_unread():
            print("Notification is unread")
        
        # Get notification age
        print(f"Created {notification.age_minutes()} minutes ago")
        
        db.close()
        ```
    """
    
    __tablename__ = "notifications"
    
    # ========================================================================
    # Primary Key
    # ========================================================================
    
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique identifier for the notification"
    )
    
    # ========================================================================
    # Foreign Keys
    # ========================================================================
    
    search_request_id = Column(
        String(36),
        ForeignKey('search_requests.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="ID of the search request this notification is about"
    )
    
    product_id = Column(
        String(36),
        ForeignKey('products.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
        comment="ID of the product this notification is about (if applicable)"
    )
    
    # ========================================================================
    # Notification Information
    # ========================================================================
    
    type = Column(
        SQLEnum(NotificationType),
        nullable=False,
        index=True,
        comment="Type of notification (match_found, search_started, etc.)"
    )
    
    message = Column(
        Text,
        nullable=False,
        comment="Notification message text"
    )
    
    # ========================================================================
    # Status
    # ========================================================================
    
    read = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether the notification has been read by the user"
    )
    
    # ========================================================================
    # Timestamps
    # ========================================================================
    
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When the notification was created"
    )
    
    # ========================================================================
    # Relationships
    # ========================================================================
    
    # Many-to-one: Multiple notifications belong to one search request
    # NOTE: This will be uncommented after SearchRequest model is updated
    # search_request = relationship(
    #     "SearchRequest",
    #     back_populates="notifications"
    # )
    
    # Many-to-one: Multiple notifications can reference one product
    # NOTE: This will be uncommented after Product model is updated
    # product = relationship(
    #     "Product",
    #     back_populates="notifications"
    # )
    
    # ========================================================================
    # Indexes for Performance
    # ========================================================================
    
    __table_args__ = (
        # Composite index for finding unread notifications
        Index('idx_notifications_unread', 'read', 'created_at'),
        # Composite index for notifications by search and type
        Index('idx_notifications_search_type', 'search_request_id', 'type'),
    )
    
    # ========================================================================
    # Methods
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of Notification."""
        return (
            f"<Notification(id={self.id}, "
            f"type={self.type.value}, "
            f"read={self.read}, "
            f"search_request_id={self.search_request_id})>"
        )
    
    def mark_as_read(self) -> None:
        """
        Mark the notification as read.
        
        Sets the read flag to True. Remember to commit the session
        after calling this method.
        
        Example:
            ```python
            notification.mark_as_read()
            db.commit()
            ```
        """
        self.read = True
    
    def mark_as_unread(self) -> None:
        """
        Mark the notification as unread.
        
        Sets the read flag to False. Remember to commit the session
        after calling this method.
        
        Example:
            ```python
            notification.mark_as_unread()
            db.commit()
            ```
        """
        self.read = False
    
    def is_read(self) -> bool:
        """
        Check if the notification has been read.
        
        Returns:
            bool: True if notification has been read, False otherwise
        
        Example:
            ```python
            if notification.is_read():
                print("User has seen this notification")
            ```
        """
        return self.read
    
    def is_unread(self) -> bool:
        """
        Check if the notification is unread.
        
        Returns:
            bool: True if notification is unread, False otherwise
        
        Example:
            ```python
            if notification.is_unread():
                print("New notification!")
            ```
        """
        return not self.read
    
    def is_match_notification(self) -> bool:
        """
        Check if this is a match found notification.
        
        Returns:
            bool: True if type is MATCH_FOUND, False otherwise
        
        Example:
            ```python
            if notification.is_match_notification():
                print("A product match was found!")
            ```
        """
        return self.type == NotificationType.MATCH_FOUND
    
    def is_error_notification(self) -> bool:
        """
        Check if this is an error notification.
        
        Returns:
            bool: True if type is ERROR_OCCURRED, False otherwise
        
        Example:
            ```python
            if notification.is_error_notification():
                print("An error occurred during search")
            ```
        """
        return self.type == NotificationType.ERROR_OCCURRED
    
    def has_product(self) -> bool:
        """
        Check if notification is associated with a product.
        
        Returns:
            bool: True if product_id is not None, False otherwise
        
        Example:
            ```python
            if notification.has_product():
                print("This notification is about a specific product")
            ```
        """
        return self.product_id is not None
    
    def age_seconds(self) -> float:
        """
        Calculate the age of the notification in seconds.
        
        Returns:
            float: Number of seconds since notification was created
        
        Example:
            ```python
            age = notification.age_seconds()
            print(f"Notification is {age:.0f} seconds old")
            ```
        """
        delta = datetime.utcnow() - self.created_at
        return delta.total_seconds()
    
    def age_minutes(self) -> float:
        """
        Calculate the age of the notification in minutes.
        
        Returns:
            float: Number of minutes since notification was created
        
        Example:
            ```python
            age = notification.age_minutes()
            print(f"Notification is {age:.1f} minutes old")
            ```
        """
        return self.age_seconds() / 60
    
    def age_hours(self) -> float:
        """
        Calculate the age of the notification in hours.
        
        Returns:
            float: Number of hours since notification was created
        
        Example:
            ```python
            age = notification.age_hours()
            print(f"Notification is {age:.1f} hours old")
            ```
        """
        return self.age_minutes() / 60
    
    def is_recent(self, minutes: int = 60) -> bool:
        """
        Check if notification was created recently.
        
        Args:
            minutes: Number of minutes to consider as recent (default: 60)
        
        Returns:
            bool: True if notification age is less than specified minutes
        
        Example:
            ```python
            if notification.is_recent(30):
                print("This notification is less than 30 minutes old")
            ```
        """
        return self.age_minutes() < minutes
    
    def get_short_message(self, max_length: int = 50) -> str:
        """
        Get a shortened version of the message.
        
        Args:
            max_length: Maximum length of the message
        
        Returns:
            str: Shortened message with ellipsis if needed
        
        Example:
            ```python
            short_msg = notification.get_short_message(30)
            print(short_msg)
            ```
        """
        if len(self.message) <= max_length:
            return self.message
        return self.message[:max_length - 3] + "..."
    
    def to_dict(self) -> dict:
        """
        Convert the notification to a dictionary.
        
        Returns:
            dict: Dictionary representation of the notification
        
        Example:
            ```python
            notif_dict = notification.to_dict()
            print(notif_dict['type'])
            print(notif_dict['message'])
            ```
        """
        return {
            'id': self.id,
            'search_request_id': self.search_request_id,
            'product_id': self.product_id,
            'type': self.type.value,
            'message': self.message,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'age_minutes': self.age_minutes(),
            'is_recent': self.is_recent(),
        }

# Made with Bob