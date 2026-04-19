from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class EmailPreferenceBase(BaseModel):
    """Base schema with common fields"""
    email_address: EmailStr = Field(
        ..., 
        description="Email address for notifications"
    )
    notify_on_match: bool = Field(
        default=True, 
        description="Send email when match found"
    )
    notify_on_start: bool = Field(
        default=True, 
        description="Send email when search starts"
    )
    include_in_digest: bool = Field(
        default=True, 
        description="Include in daily digest"
    )


class EmailPreferenceCreate(EmailPreferenceBase):
    """Schema for creating email preferences"""
    search_request_id: int = Field(
        ..., 
        description="ID of the search request",
        gt=0
    )


class EmailPreferenceUpdate(BaseModel):
    """Schema for updating email preferences (all fields optional)"""
    email_address: Optional[EmailStr] = None
    notify_on_match: Optional[bool] = None
    notify_on_start: Optional[bool] = None
    include_in_digest: Optional[bool] = None


class EmailPreferenceResponse(EmailPreferenceBase):
    """Schema for API responses"""
    id: int
    search_request_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models