"""
Pydantic schemas for SearchExecution model.

These schemas are used for API response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """Search execution status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SearchExecutionBase(BaseModel):
    """Base schema with common execution fields."""
    search_request_id: str = Field(..., description="ID of the parent search request")
    started_at: datetime = Field(..., description="When the search execution started")
    completed_at: Optional[datetime] = Field(None, description="When the search execution completed")
    status: str = Field(..., description="Current status of the execution")
    products_found: int = Field(default=0, ge=0, description="Total number of products found during this execution")
    matches_found: int = Field(default=0, ge=0, description="Number of products that met the match criteria")
    error_message: Optional[str] = Field(None, description="Error message if the execution failed")


class SearchExecutionResponse(SearchExecutionBase):
    """Schema for search execution API responses."""
    id: str = Field(..., description="Unique identifier for the search execution")
    duration_seconds: float = Field(..., ge=0, description="Duration of the execution in seconds")
    match_rate: float = Field(..., ge=0, le=100, description="Percentage of products that were matches")

    class Config:
        from_attributes = True  # Allows creation from ORM models


class SearchExecutionListResponse(BaseModel):
    """Schema for paginated list of search executions."""
    items: list[SearchExecutionResponse]
    total: int
    page: int = 1
    page_size: int = 50


class SearchExecutionSummary(BaseModel):
    """Schema for execution summary statistics."""
    total_executions: int = Field(..., description="Total number of executions")
    successful_executions: int = Field(..., description="Number of successful executions")
    failed_executions: int = Field(..., description="Number of failed executions")
    total_products_found: int = Field(..., description="Total products found across all executions")
    total_matches_found: int = Field(..., description="Total matches found across all executions")
    average_match_rate: float = Field(..., description="Average match rate across all executions")
    last_execution: Optional[SearchExecutionResponse] = Field(None, description="Most recent execution")


class SearchExecutionFilterParams(BaseModel):
    """Schema for execution filtering parameters."""
    search_request_id: Optional[str] = Field(None, description="Filter by search request")
    status: Optional[ExecutionStatus] = Field(None, description="Filter by status")
    min_matches: Optional[int] = Field(None, ge=0, description="Minimum number of matches")
    start_date: Optional[datetime] = Field(None, description="Filter executions after this date")
    end_date: Optional[datetime] = Field(None, description="Filter executions before this date")

# Made with Bob
