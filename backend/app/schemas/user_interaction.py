"""
Pydantic schemas for UserInteraction API validation.

These schemas are used for request/response validation in the API endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class UserInteractionBase(BaseModel):
    """Base schema for UserInteraction with common fields."""
    
    user_id: str = Field(
        ...,
        description="User identifier (session ID or account ID)",
        min_length=1,
        max_length=255
    )
    product_id: str = Field(
        ...,
        description="ID of the product that was interacted with (UUID)",
        min_length=1,
        max_length=36
    )
    interaction_type: str = Field(
        ...,
        description="Type of interaction: 'view', 'click', 'ignore', 'purchase'",
        pattern="^(view|click|ignore|purchase)$"
    )
    duration_seconds: int = Field(
        default=0,
        description="How long the user viewed the product (in seconds)",
        ge=0
    )
    interaction_metadata: Optional[str] = Field(
        default=None,
        description="Optional JSON string with additional interaction data",
        max_length=1000
    )


class UserInteractionCreate(UserInteractionBase):
    """
    Schema for creating a new user interaction.
    
    Example:
        ```python
        interaction = UserInteractionCreate(
            user_id="user123",
            product_id=456,
            interaction_type="click",
            duration_seconds=30
        )
        ```
    """
    pass


class UserInteractionResponse(UserInteractionBase):
    """
    Schema for user interaction responses.
    
    Includes all fields plus the ID and timestamp.
    """
    
    id: int = Field(..., description="Unique identifier for the interaction")
    timestamp: datetime = Field(..., description="When the interaction occurred")
    
    class Config:
        from_attributes = True  # Allows creation from ORM models


class UserInteractionListResponse(BaseModel):
    """
    Schema for paginated list of user interactions.
    
    Example:
        ```python
        response = UserInteractionListResponse(
            interactions=[interaction1, interaction2],
            total=100,
            page=1,
            page_size=20
        )
        ```
    """
    
    interactions: list[UserInteractionResponse] = Field(
        ...,
        description="List of user interactions"
    )
    total: int = Field(..., description="Total number of interactions", ge=0)
    page: int = Field(default=1, description="Current page number", ge=1)
    page_size: int = Field(default=20, description="Number of items per page", ge=1, le=100)


class UserInteractionStats(BaseModel):
    """
    Schema for user interaction statistics.
    
    Example:
        ```python
        stats = UserInteractionStats(
            total_interactions=150,
            total_views=100,
            total_clicks=40,
            total_purchases=10,
            click_through_rate=0.4,
            purchase_rate=0.1,
            avg_view_duration=25.5
        )
        ```
    """
    
    total_interactions: int = Field(..., description="Total number of interactions", ge=0)
    total_views: int = Field(..., description="Total number of views", ge=0)
    total_clicks: int = Field(..., description="Total number of clicks", ge=0)
    total_purchases: int = Field(..., description="Total number of purchases", ge=0)
    click_through_rate: float = Field(..., description="Click-through rate (0.0 to 1.0)", ge=0.0, le=1.0)
    purchase_rate: float = Field(..., description="Purchase rate (0.0 to 1.0)", ge=0.0, le=1.0)
    avg_view_duration: float = Field(..., description="Average view duration in seconds", ge=0.0)


class UserInteractionFilterParams(BaseModel):
    """
    Schema for filtering user interactions.
    
    Example:
        ```python
        filters = UserInteractionFilterParams(
            user_id="user123",
            interaction_type="click",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
        ```
    """
    
    user_id: Optional[str] = Field(
        default=None,
        description="Filter by user ID"
    )
    product_id: Optional[str] = Field(
        default=None,
        description="Filter by product ID (UUID)",
        min_length=1,
        max_length=36
    )
    interaction_type: Optional[str] = Field(
        default=None,
        description="Filter by interaction type",
        pattern="^(view|click|ignore|purchase)$"
    )
    start_date: Optional[datetime] = Field(
        default=None,
        description="Filter interactions after this date"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="Filter interactions before this date"
    )
    page: int = Field(default=1, description="Page number", ge=1)
    page_size: int = Field(default=20, description="Items per page", ge=1, le=100)
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure end_date is after start_date if both are provided."""
        if v and info.data.get('start_date') and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


# Made with Bob