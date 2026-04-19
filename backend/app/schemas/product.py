"""
Pydantic schemas for Product model.

These schemas are used for API response serialization.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """Base schema with common product fields."""
    title: str = Field(..., description="Product title or name")
    description: Optional[str] = Field(None, description="Detailed product description")
    price: float = Field(..., ge=0, description="Product price in dollars (0 for free items or unknown price)")
    url: str = Field(..., description="URL to the product listing")
    image_url: Optional[str] = Field(None, description="URL to the product image")
    platform: str = Field(..., description="Platform where product was found (craigslist, facebook, ebay)")
    location: Optional[str] = Field(None, description="Geographic location of the product")
    posted_date: Optional[datetime] = Field(None, description="When the product was originally posted")


class ProductResponse(ProductBase):
    """Schema for product API responses."""
    id: str = Field(..., description="Unique identifier for the product")
    search_execution_id: str = Field(..., description="ID of the search execution that found this product")
    match_score: Optional[float] = Field(None, ge=0, le=100, description="Similarity score (0-100) compared to search criteria")
    is_match: bool = Field(..., description="Whether product meets the match threshold")
    created_at: datetime = Field(..., description="When the product was scraped and saved")

    class Config:
        from_attributes = True  # Allows creation from ORM models


class ProductListResponse(BaseModel):
    """Schema for paginated list of products."""
    items: list[ProductResponse]
    total: int
    page: int = 1
    page_size: int = 50


class ProductMatchResponse(ProductResponse):
    """Schema for product match responses with additional context."""
    days_since_posted: int = Field(..., description="Number of days since product was posted")
    is_recent: bool = Field(..., description="Whether product was posted recently (within 7 days)")
    is_within_budget: bool = Field(..., description="Whether product price is within search budget")


class ProductFilterParams(BaseModel):
    """Schema for product filtering parameters."""
    platform: Optional[str] = Field(None, description="Filter by platform")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    is_match: Optional[bool] = Field(None, description="Filter by match status")
    min_match_score: Optional[float] = Field(None, ge=0, le=100, description="Minimum match score")
    location: Optional[str] = Field(None, description="Filter by location")
    search_execution_id: Optional[str] = Field(None, description="Filter by search execution")

# Made with Bob
