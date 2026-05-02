"""
Pydantic schemas for UserPreference API validation.

These schemas are used for request/response validation in the API endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Dict, Any
import json


class UserPreferenceBase(BaseModel):
    """Base schema for UserPreference with common fields."""
    
    user_id: str = Field(
        ...,
        description="User identifier (session ID or account ID)",
        min_length=1,
        max_length=255
    )
    preference_type: str = Field(
        ...,
        description="Type of preference (e.g., 'price_sensitivity', 'platform_preference')",
        min_length=1,
        max_length=100
    )
    preference_value: str = Field(
        ...,
        description="JSON string containing the preference data",
        max_length=2000
    )
    confidence_score: float = Field(
        default=0.0,
        description="Confidence in this preference (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    @field_validator('preference_value')
    @classmethod
    def validate_json(cls, v):
        """Ensure preference_value is valid JSON."""
        try:
            json.loads(v)
            return v
        except json.JSONDecodeError:
            raise ValueError('preference_value must be valid JSON string')


class UserPreferenceCreate(UserPreferenceBase):
    """
    Schema for creating a new user preference.
    
    Example:
        ```python
        import json
        
        preference = UserPreferenceCreate(
            user_id="user123",
            preference_type="price_sensitivity",
            preference_value=json.dumps({
                'avg_price': 450.0,
                'max_price': 600.0,
                'min_price': 300.0
            }),
            confidence_score=0.75
        )
        ```
    """
    pass


class UserPreferenceUpdate(BaseModel):
    """
    Schema for updating an existing user preference.
    
    All fields are optional to allow partial updates.
    """
    
    preference_value: Optional[str] = Field(
        default=None,
        description="JSON string containing the preference data",
        max_length=2000
    )
    confidence_score: Optional[float] = Field(
        default=None,
        description="Confidence in this preference (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    @field_validator('preference_value')
    @classmethod
    def validate_json(cls, v):
        """Ensure preference_value is valid JSON if provided."""
        if v is not None:
            try:
                json.loads(v)
                return v
            except json.JSONDecodeError:
                raise ValueError('preference_value must be valid JSON string')
        return v


class UserPreferenceResponse(UserPreferenceBase):
    """
    Schema for user preference responses.
    
    Includes all fields plus the ID and last_updated timestamp.
    """
    
    id: int = Field(..., description="Unique identifier for the preference")
    last_updated: datetime = Field(..., description="When this preference was last updated")
    
    class Config:
        from_attributes = True  # Allows creation from ORM models


class UserPreferenceListResponse(BaseModel):
    """
    Schema for list of user preferences.
    
    Example:
        ```python
        response = UserPreferenceListResponse(
            preferences=[pref1, pref2],
            total=10
        )
        ```
    """
    
    preferences: list[UserPreferenceResponse] = Field(
        ...,
        description="List of user preferences"
    )
    total: int = Field(..., description="Total number of preferences", ge=0)


class UserPreferenceWeights(BaseModel):
    """
    Schema for learned preference weights used in scoring.
    
    This is the output format from PreferenceLearner.get_preference_weights()
    
    Example:
        ```python
        weights = UserPreferenceWeights(
            price_sensitivity=0.8,
            condition_importance=0.6,
            location_preference=0.3,
            platform_scores={'craigslist': 0.8, 'ebay': 0.5},
            preferred_features=['leather', 'warranty'],
            location_scores={'Boston': 0.9, 'Cambridge': 0.7}
        )
        ```
    """
    
    price_sensitivity: float = Field(
        default=0.5,
        description="How sensitive the user is to price (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    condition_importance: float = Field(
        default=0.5,
        description="How important product condition is (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    location_preference: float = Field(
        default=0.3,
        description="How important location is (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    platform_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Preference scores for each platform"
    )
    preferred_features: list[str] = Field(
        default_factory=list,
        description="List of preferred product features"
    )
    location_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Preference scores for each location"
    )


class UserPreferenceFilterParams(BaseModel):
    """
    Schema for filtering user preferences.
    
    Example:
        ```python
        filters = UserPreferenceFilterParams(
            user_id="user123",
            preference_type="price_sensitivity"
        )
        ```
    """
    
    user_id: Optional[str] = Field(
        default=None,
        description="Filter by user ID"
    )
    preference_type: Optional[str] = Field(
        default=None,
        description="Filter by preference type"
    )
    min_confidence: Optional[float] = Field(
        default=None,
        description="Filter by minimum confidence score",
        ge=0.0,
        le=1.0
    )


# Made with Bob