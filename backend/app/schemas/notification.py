"""
Pydantic schemas for Notification model.

These schemas are used for API response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Notification type enum."""
    MATCH_FOUND = "match_found"
    SEARCH_STARTED = "search_started"
    SEARCH_COMPLETED = "search_completed"
    ERROR_OCCURRED = "error_occurred"


class NotificationBase(BaseModel):
    """Base schema with common notification fields."""
    search_request_id: str = Field(..., description="ID of the search request this notification is about")
    product_id: Optional[str] = Field(None, description="ID of the product this notification is about (if applicable)")
    type: NotificationType = Field(..., description="Type of notification")
    message: str = Field(..., description="Notification message text")
    read: bool = Field(default=False, description="Whether the notification has been read by the user")


class NotificationResponse(NotificationBase):
    """Schema for notification API responses."""
    id: str = Field(..., description="Unique identifier for the notification")
    created_at: datetime = Field(..., description="When the notification was created")
    age_minutes: float = Field(..., ge=0, description="Age of notification in minutes")
    is_recent: bool = Field(..., description="Whether notification was created recently (within 60 minutes)")

    class Config:
        from_attributes = True  # Allows creation from ORM models


class NotificationListResponse(BaseModel):
    """Schema for paginated list of notifications."""
    items: list[NotificationResponse]
    total: int
    unread_count: int = Field(..., description="Number of unread notifications")
    page: int = 1
    page_size: int = 50


class NotificationMarkReadRequest(BaseModel):
    """Schema for marking notifications as read."""
    notification_ids: list[str] = Field(..., description="List of notification IDs to mark as read")


class NotificationFilterParams(BaseModel):
    """Schema for notification filtering parameters."""
    search_request_id: Optional[str] = Field(None, description="Filter by search request")
    product_id: Optional[str] = Field(None, description="Filter by product")
    type: Optional[NotificationType] = Field(None, description="Filter by notification type")
    read: Optional[bool] = Field(None, description="Filter by read status")
    is_recent: Optional[bool] = Field(None, description="Filter recent notifications only")


class NotificationStats(BaseModel):
    """Schema for notification statistics."""
    total_notifications: int = Field(..., description="Total number of notifications")
    unread_notifications: int = Field(..., description="Number of unread notifications")
    match_notifications: int = Field(..., description="Number of match found notifications")
    error_notifications: int = Field(..., description="Number of error notifications")
    recent_notifications: int = Field(..., description="Number of recent notifications (within 60 minutes)")

# ========================================================================
# WebSocket-Specific Schemas
# ========================================================================

class WebSocketNotificationBase(BaseModel):
    """Base schema for WebSocket notifications."""
    type: NotificationType = Field(..., description="Type of notification")
    message: str = Field(..., description="Notification message text")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When notification was sent")


class WebSocketMatchFoundNotification(WebSocketNotificationBase):
    """WebSocket notification when new product match is found."""
    type: NotificationType = NotificationType.MATCH_FOUND
    search_request_id: str = Field(..., description="ID of the search request")
    product_id: str = Field(..., description="ID of the matched product")
    product_title: str = Field(..., description="Title of the matched product")
    product_price: float = Field(..., description="Price of the matched product")
    product_url: str = Field(..., description="URL to the product listing")
    match_score: float = Field(..., ge=0, le=100, description="Match score (0-100)")
    platform: str = Field(..., description="Platform where product was found")


class WebSocketSearchStatusNotification(WebSocketNotificationBase):
    """WebSocket notification for search status updates."""
    search_request_id: str = Field(..., description="ID of the search request")
    search_execution_id: Optional[str] = Field(None, description="ID of the search execution")
    status: str = Field(..., description="Current status of the search")
    matches_found: Optional[int] = Field(None, description="Number of matches found (for completed searches)")


class WebSocketErrorNotification(WebSocketNotificationBase):
    """WebSocket notification for errors."""
    type: NotificationType = NotificationType.ERROR_OCCURRED
    search_request_id: Optional[str] = Field(None, description="ID of the search request (if applicable)")
    error_details: Optional[str] = Field(None, description="Detailed error information")
    error_code: Optional[str] = Field(None, description="Error code for categorization")


class WebSocketHeartbeat(BaseModel):
    """WebSocket heartbeat/ping message."""
    type: str = Field(default="heartbeat", description="Message type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current server time")
    server_status: str = Field(default="ok", description="Server status")
