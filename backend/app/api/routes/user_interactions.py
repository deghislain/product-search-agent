"""
API routes for user interactions and preferences.

These endpoints allow tracking user behavior and retrieving learned preferences.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import Optional
from datetime import datetime

from app.api.dependencies import get_db
from app.models.user_interaction import UserInteraction
from app.models.user_preference import UserPreference
from app.models.product import Product
from app.schemas.user_interaction import (
    UserInteractionCreate,
    UserInteractionResponse,
    UserInteractionListResponse,
    UserInteractionStats,
    UserInteractionFilterParams,
)
from app.schemas.user_preference import (
    UserPreferenceResponse,
    UserPreferenceListResponse,
    UserPreferenceWeights,
    UserPreferenceFilterParams,
)
from app.core.preference_learner import PreferenceLearner

router = APIRouter(prefix="/api/user-interactions", tags=["User Interactions"])


@router.post("/", response_model=UserInteractionResponse, status_code=201)
async def track_interaction(
    interaction: UserInteractionCreate,
    db: Session = Depends(get_db)
):
    """
    Track a user interaction with a product.
    
    This endpoint records user behavior (view, click, ignore, purchase) and
    updates the user's learned preferences accordingly.
    
    Args:
        interaction: The interaction data to record
        db: Database session
    
    Returns:
        The created interaction record
    
    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/user-interactions/" \\
          -H "Content-Type: application/json" \\
          -d '{
            "user_id": "user123",
            "product_id": 456,
            "interaction_type": "click",
            "duration_seconds": 30
          }'
        ```
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == interaction.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Use PreferenceLearner to track interaction
    learner = PreferenceLearner(db=db)
    
    try:
        db_interaction = await learner.track_interaction(
            user_id=interaction.user_id,
            product=product,
            action=interaction.interaction_type,
            duration_seconds=interaction.duration_seconds,
            metadata={"raw": interaction.interaction_metadata} if interaction.interaction_metadata else None
        )
        
        return db_interaction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking interaction: {str(e)}")


@router.get("/", response_model=UserInteractionListResponse)
async def list_interactions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    interaction_type: Optional[str] = Query(None, description="Filter by interaction type"),
    start_date: Optional[datetime] = Query(None, description="Filter interactions after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter interactions before this date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List user interactions with optional filtering.
    
    Returns a paginated list of user interactions based on the provided filters.
    
    Example:
        ```bash
        curl "http://localhost:8000/api/user-interactions/?user_id=user123&page=1&page_size=20"
        ```
    """
    # Build query
    query = db.query(UserInteraction)
    
    # Apply filters
    if user_id:
        query = query.filter(UserInteraction.user_id == user_id)
    if product_id:
        query = query.filter(UserInteraction.product_id == product_id)
    if interaction_type:
        query = query.filter(UserInteraction.interaction_type == interaction_type)
    if start_date:
        query = query.filter(UserInteraction.timestamp >= start_date)
    if end_date:
        query = query.filter(UserInteraction.timestamp <= end_date)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    interactions = query.order_by(desc(UserInteraction.timestamp)).offset(offset).limit(page_size).all()
    
    return UserInteractionListResponse(
        interactions=interactions,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/stats/{user_id}", response_model=UserInteractionStats)
async def get_user_stats(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get interaction statistics for a specific user.
    
    Returns aggregated statistics about the user's interaction patterns.
    
    Example:
        ```bash
        curl "http://localhost:8000/api/user-interactions/stats/user123"
        ```
    """
    learner = PreferenceLearner(db=db)
    
    try:
        stats = await learner.get_user_stats(user_id)
        return UserInteractionStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user stats: {str(e)}")


@router.get("/preferences/{user_id}", response_model=UserPreferenceListResponse)
async def get_user_preferences(
    user_id: str,
    preference_type: Optional[str] = Query(None, description="Filter by preference type"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence score"),
    db: Session = Depends(get_db)
):
    """
    Get learned preferences for a specific user.
    
    Returns all preference records for the user, optionally filtered by type and confidence.
    
    Example:
        ```bash
        curl "http://localhost:8000/api/user-interactions/preferences/user123"
        ```
    """
    # Build query
    query = db.query(UserPreference).filter(UserPreference.user_id == user_id)
    
    # Apply filters
    if preference_type:
        query = query.filter(UserPreference.preference_type == preference_type)
    if min_confidence is not None:
        query = query.filter(UserPreference.confidence_score >= min_confidence)
    
    preferences = query.order_by(desc(UserPreference.last_updated)).all()
    
    return UserPreferenceListResponse(
        preferences=preferences,
        total=len(preferences)
    )


@router.get("/preferences/{user_id}/weights", response_model=UserPreferenceWeights)
async def get_preference_weights(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get preference weights for scoring products.
    
    Returns the learned preference weights that can be used to adjust
    product matching scores based on user behavior.
    
    Example:
        ```bash
        curl "http://localhost:8000/api/user-interactions/preferences/user123/weights"
        ```
    """
    learner = PreferenceLearner(db=db)
    
    try:
        weights = await learner.get_preference_weights(user_id)
        return UserPreferenceWeights(**weights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting preference weights: {str(e)}")


@router.delete("/{interaction_id}", status_code=204)
async def delete_interaction(
    interaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific user interaction.
    
    This is useful for removing erroneous or test data.
    
    Example:
        ```bash
        curl -X DELETE "http://localhost:8000/api/user-interactions/123"
        ```
    """
    interaction = db.query(UserInteraction).filter(UserInteraction.id == interaction_id).first()
    
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    db.delete(interaction)
    db.commit()
    
    return None


# Made with Bob