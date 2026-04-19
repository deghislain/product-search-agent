from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class EmailPreference(Base):  # ✅ SQLAlchemy model
    __tablename__ = "email_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    search_request_id = Column(
        Integer, 
        ForeignKey("search_requests.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    email_address = Column(String, nullable=False, index=True)
    notify_on_match = Column(Boolean, default=True, nullable=False)
    notify_on_start = Column(Boolean, default=True, nullable=False)
    include_in_digest = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    # Relationship to SearchRequest
    search_request = relationship("SearchRequest", back_populates="email_preferences")
    
    def __repr__(self):
        return f"<EmailPreference(id={self.id}, email={self.email_address})>"
