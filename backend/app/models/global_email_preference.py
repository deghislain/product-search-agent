from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class GlobalEmailPreference(Base):
    """
    Global email preferences not tied to specific searches.
    One record per user (identified by email).
    """
    __tablename__ = "global_email_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    email_address = Column(String, unique=True, nullable=False, index=True)
    
    # Notification settings
    notify_on_match = Column(Boolean, default=True, nullable=False)
    notify_on_start = Column(Boolean, default=False, nullable=False)
    include_in_digest = Column(Boolean, default=True, nullable=False)
    
    # Digest settings
    digest_time = Column(String, default="09:00", nullable=False)  # Format: "HH:MM"
    digest_timezone = Column(String, default="UTC", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)