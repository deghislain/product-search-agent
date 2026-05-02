"""
UserPreference model for storing learned user preferences.

This model stores aggregated preference data learned from user interactions,
such as price sensitivity, platform preferences, and feature preferences.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from datetime import datetime

from app.database import Base


class UserPreference(Base):
    """
    UserPreference model for storing learned preferences.
    
    Stores aggregated preference data learned from analyzing user interactions:
    - Price sensitivity
    - Platform preferences
    - Location preferences
    - Feature preferences
    - Brand loyalty
    
    Attributes:
        id (int): Unique identifier
        user_id (str): User identifier
        preference_type (str): Type of preference (e.g., 'price_sensitivity', 'platform_preference')
        preference_value (str): JSON string containing the preference data
        confidence_score (float): Confidence in this preference (0.0 to 1.0)
        last_updated (datetime): When this preference was last updated
    
    Example:
        ```python
        from app.models import UserPreference
        from app.database import SessionLocal
        import json
        
        # Store price sensitivity preference
        preference = UserPreference(
            user_id="user123",
            preference_type="price_sensitivity",
            preference_value=json.dumps({
                'avg_price': 450.0,
                'max_price': 600.0,
                'min_price': 300.0
            }),
            confidence_score=0.75,
            last_updated=datetime.utcnow()
        )
        
        db = SessionLocal()
        db.add(preference)
        db.commit()
        db.close()
        ```
    """
    
    __tablename__ = "user_preferences"
    
    # ========================================================================
    # Primary Key
    # ========================================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Unique identifier for the preference"
    )
    
    # ========================================================================
    # User Reference
    # ========================================================================
    
    user_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="User identifier (session ID or account ID)"
    )
    
    # ========================================================================
    # Preference Data
    # ========================================================================
    
    preference_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of preference: 'price_sensitivity', 'platform_preference', etc."
    )
    
    preference_value = Column(
        String(2000),
        nullable=False,
        comment="JSON string containing the preference data"
    )
    
    confidence_score = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="Confidence in this preference (0.0 to 1.0)"
    )
    
    last_updated = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        index=True,
        comment="When this preference was last updated"
    )
    
    # ========================================================================
    # Indexes for Performance
    # ========================================================================
    
    __table_args__ = (
        # Composite index for user preference queries
        Index('idx_user_preferences_user_type', 'user_id', 'preference_type'),
        # Unique constraint to prevent duplicate preference types per user
        Index('idx_user_preferences_unique', 'user_id', 'preference_type', unique=True),
    )
    
    # ========================================================================
    # Methods
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of UserPreference."""
        return (
            f"<UserPreference(id={self.id}, "
            f"user_id={self.user_id}, "
            f"type={self.preference_type}, "
            f"confidence={self.confidence_score:.2f})>"
        )
    
    def to_dict(self) -> dict:
        """
        Convert the preference to a dictionary.
        
        Returns:
            dict: Dictionary representation of the preference
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'preference_type': self.preference_type,
            'preference_value': self.preference_value,
            'confidence_score': self.confidence_score,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        }


# Made with Bob