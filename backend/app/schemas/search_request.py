"""
Pydantic schemas for SearchRequest model.

These schemas are used for API request validation and response serialization.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class SearchStatus(str, Enum):
    """Search request status enum."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SearchRequestBase(BaseModel):
    """Base schema with common fields."""
    product_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name or title of the product to search for"
    )
    product_description: str = Field(
        ...,
        min_length=1,
        description="Detailed description of the desired product"
    )
    budget: float = Field(
        ...,
        gt=0,
        description="Maximum price willing to pay"
    )
    location: Optional[str] = Field(
        None,
        max_length=255,
        description="Geographic location for search (e.g., 'Boston, MA')"
    )
    match_threshold: float = Field(
        default=70.0,
        ge=0,
        le=100,
        description="Minimum similarity score (0-100) for a product to be considered a match"
    )
    search_craigslist: bool = Field(
        default=False,
        description="Enable the search on Craigslist"
    )
    search_ebay: bool = Field(
        default=False,
        description="Enable the search on eBay"
    )
    search_facebook: bool = Field(
        default=False,
        description="Enable the search on Facebook Marketplace"
    )


class SearchRequestCreate(SearchRequestBase):
    """Schema for creating a new search request."""
    pass


class SearchRequestUpdate(BaseModel):
    """Schema for updating an existing search request."""
    product_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Name or title of the product to search for"
    )
    product_description: Optional[str] = Field(
        None,
        min_length=1,
        description="Detailed description of the desired product"
    )
    budget: Optional[float] = Field(
        None,
        gt=0,
        description="Maximum price willing to pay"
    )
    location: Optional[str] = Field(
        None,
        max_length=255,
        description="Geographic location for search"
    )
    match_threshold: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Minimum similarity score for matches"
    )
    status: Optional[SearchStatus] = Field(
        None,
        description="Current status of the search request"
    )
    search_craigslist: Optional[bool] = Field(
        None,
        description="Enable the search on Craigslist"
    )
    search_ebay: Optional[bool] = Field(
        None,
        description="Enable the search on eBay"
    )
    search_facebook: Optional[bool] = Field(
        None,
        description="Enable the search on Facebook Marketplace"
    )

class SearchRequestResponse(SearchRequestBase):
    """Schema for search request API responses."""
    id: str = Field(..., description="Unique identifier for the search request")
    status: SearchStatus = Field(..., description="Current status of the search request")
    created_at: datetime = Field(..., description="When the search request was created")
    updated_at: datetime = Field(..., description="When the search request was last updated")

    class Config:
        from_attributes = True  # Allows creation from ORM models


class SearchRequestListResponse(BaseModel):
    """Schema for paginated list of search requests."""
    items: list[SearchRequestResponse]
    total: int
    page: int = 1
    page_size: int = 50


class SearchRequestStatusUpdate(BaseModel):
    """Schema for updating search request status."""
    status: SearchStatus = Field(..., description="New status for the search request")

# Made with Bob
