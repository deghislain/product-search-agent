"""
Pydantic schemas package for API request/response validation.

This package contains all Pydantic schemas used for:
- Request validation
- Response serialization
- Data validation before database operations
"""

# Search Request schemas
from app.schemas.search_request import (
    SearchStatus,
    SearchRequestBase,
    SearchRequestCreate,
    SearchRequestUpdate,
    SearchRequestResponse,
    SearchRequestListResponse,
    SearchRequestStatusUpdate,
)

# Product schemas
from app.schemas.product import (
    ProductBase,
    ProductResponse,
    ProductListResponse,
    ProductMatchResponse,
    ProductFilterParams,
)

# Search Execution schemas
from app.schemas.search_execution import (
    ExecutionStatus,
    SearchExecutionBase,
    SearchExecutionResponse,
    SearchExecutionListResponse,
    SearchExecutionSummary,
    SearchExecutionFilterParams,
)

# Notification schemas
from app.schemas.notification import (
    NotificationType,
    NotificationBase,
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkReadRequest,
    NotificationFilterParams,
    NotificationStats,
)
from app.schemas.email_preference import (
    EmailPreferenceBase,
    EmailPreferenceCreate,
    EmailPreferenceUpdate,
    EmailPreferenceResponse,
)

# User Interaction schemas
from app.schemas.user_interaction import (
    UserInteractionBase,
    UserInteractionCreate,
    UserInteractionResponse,
    UserInteractionListResponse,
    UserInteractionStats,
    UserInteractionFilterParams,
)

# User Preference schemas
from app.schemas.user_preference import (
    UserPreferenceBase,
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceResponse,
    UserPreferenceListResponse,
    UserPreferenceWeights,
    UserPreferenceFilterParams,
)

__all__ = [
    # Search Request
    "SearchStatus",
    "SearchRequestBase",
    "SearchRequestCreate",
    "SearchRequestUpdate",
    "SearchRequestResponse",
    "SearchRequestListResponse",
    "SearchRequestStatusUpdate",
    # Product
    "ProductBase",
    "ProductResponse",
    "ProductListResponse",
    "ProductMatchResponse",
    "ProductFilterParams",
    # Search Execution
    "ExecutionStatus",
    "SearchExecutionBase",
    "SearchExecutionResponse",
    "SearchExecutionListResponse",
    "SearchExecutionSummary",
    "SearchExecutionFilterParams",
    # Notification
    "NotificationType",
    "NotificationBase",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationMarkReadRequest",
    "NotificationFilterParams",
    "NotificationStats",
    # Email Preference
    "EmailPreferenceBase",
    "EmailPreferenceCreate",
    "EmailPreferenceUpdate",
    "EmailPreferenceResponse",
    # User Interaction
    "UserInteractionBase",
    "UserInteractionCreate",
    "UserInteractionResponse",
    "UserInteractionListResponse",
    "UserInteractionStats",
    "UserInteractionFilterParams",
    # User Preference
    "UserPreferenceBase",
    "UserPreferenceCreate",
    "UserPreferenceUpdate",
    "UserPreferenceResponse",
    "UserPreferenceListResponse",
    "UserPreferenceWeights",
    "UserPreferenceFilterParams",
]

# Made with Bob
