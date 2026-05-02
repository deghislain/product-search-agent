"""
UserInteraction model for tracking user interactions with products.

This model records how users interact with products (view, click, purchase, ignore)
to learn their preferences over time.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from datetime import datetime

from app.database import Base


class UserInteraction(Base):
    """
    UserInteraction model for tracking user behavior.
    
    Records user interactions with products to learn preferences:
    - Which products they view
    - Which they click
    - Which they ignore
    - Which they purchase
    - How long they spend viewing
    
    Attributes:
        id (int): Unique identifier
        user_id (str): User identifier (can be session ID or user account ID)
        product_id (int): Foreign key to Product
        interaction_type (str): Type of interaction ('view', 'click', 'ignore', 'purchase')
        timestamp (datetime): When the interaction occurred
        duration_seconds (int): How long the user viewed the product
        metadata (str): Optional JSON string with additional data
    
    Example:
        ```python
        from app.models import UserInteraction
        from app.database import SessionLocal
        
        # Track a product view
        interaction = UserInteraction(
            user_id="user123",
            product_id=456,
            interaction_type="view",
            timestamp=datetime.utcnow(),
            duration_seconds=30
        )
        
        db = SessionLocal()
        db.add(interaction)
        db.commit()
        db.close()
        ```
    """
    
    __tablename__ = "user_interactions"
    
    # ========================================================================
    # Primary Key
    # ========================================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Unique identifier for the interaction"
    )
    
    # ========================================================================
    # User and Product References
    # ========================================================================
    
    user_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="User identifier (session ID or account ID)"
    )
    
    product_id = Column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID of the product that was interacted with"
    )
    
    # ========================================================================
    # Interaction Details
    # ========================================================================
    
    interaction_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of interaction: 'view', 'click', 'ignore', 'purchase'"
    )
    
    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When the interaction occurred"
    )
    
    duration_seconds = Column(
        Integer,
        nullable=False,
        default=0,
        comment="How long the user viewed the product (in seconds)"
    )
    
    interaction_metadata = Column(
        String(1000),
        nullable=True,
        comment="Optional JSON string with additional interaction data"
    )
    
    # ========================================================================
    # Indexes for Performance
    # ========================================================================
    
    __table_args__ = (
        # Composite index for user interaction queries
        Index('idx_user_interactions_user_type', 'user_id', 'interaction_type'),
        # Index for time-based queries
        Index('idx_user_interactions_timestamp', 'timestamp'),
        # Index for product-based queries
        Index('idx_user_interactions_product', 'product_id', 'interaction_type'),
    )
    
    # ========================================================================
    # Methods
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of UserInteraction."""
        return (
            f"<UserInteraction(id={self.id}, "
            f"user_id={self.user_id}, "
            f"product_id={self.product_id}, "
            f"type={self.interaction_type})>"
        )
    
    def to_dict(self) -> dict:
        """
        Convert the interaction to a dictionary.
        
        Returns:
            dict: Dictionary representation of the interaction
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'interaction_type': self.interaction_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'duration_seconds': self.duration_seconds,
            'interaction_metadata': self.interaction_metadata,
        }


# Made with Bob
