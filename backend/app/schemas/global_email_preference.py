from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class GlobalEmailPreferenceBase(BaseModel):
    """Base schema with common fields"""
    email_address: EmailStr
    notify_on_match: bool = True
    notify_on_start: bool = False
    include_in_digest: bool = True
    digest_time: str = "09:00"  # Format: "HH:MM"
    digest_timezone: str = "UTC"

class GlobalEmailPreferenceCreate(GlobalEmailPreferenceBase):
    """Schema for creating new preferences"""
    pass

class GlobalEmailPreferenceUpdate(BaseModel):
    """Schema for updating preferences (all fields optional)"""
    notify_on_match: Optional[bool] = None
    notify_on_start: Optional[bool] = None
    include_in_digest: Optional[bool] = None
    digest_time: Optional[str] = None
    digest_timezone: Optional[str] = None

class GlobalEmailPreferenceResponse(GlobalEmailPreferenceBase):
    """Schema for API responses"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy model