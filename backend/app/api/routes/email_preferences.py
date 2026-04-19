
"""
Email Preferences API Routes

Endpoints for managing email notification preferences for search requests.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.email_preference import EmailPreference
from app.models.search_request import SearchRequest
from app.schemas.email_preference import (
    EmailPreferenceCreate,
    EmailPreferenceUpdate,
    EmailPreferenceResponse
)
from app.database import get_db

router = APIRouter(prefix="/api/email-preferences", tags=["email"])


@router.post(
    "/",
    response_model=EmailPreferenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create email preferences",
    description="Create email notification preferences for a search request"
)
def create_email_preference(
    preference: EmailPreferenceCreate,
    db: Session = Depends(get_db)
):
    """
    Create email notification preferences for a search request.
    
    Args:
        preference: Email preference data including search_request_id and notification settings
        db: Database session
        
    Returns:
        EmailPreferenceResponse: Created email preference
        
    Raises:
        HTTPException 404: If search request not found
        HTTPException 400: If preferences already exist for this search request
    """
    # Verify search request exists
    search_request = db.query(SearchRequest).filter(
        SearchRequest.id == preference.search_request_id
    ).first()
    
    if not search_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search request with id {preference.search_request_id} not found"
        )
    
    # Check if preferences already exist
    existing = db.query(EmailPreference).filter(
        EmailPreference.search_request_id == preference.search_request_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email preferences already exist for search request {preference.search_request_id}"
        )
    
    # Create new preferences
    db_preference = EmailPreference(**preference.model_dump())
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    
    return db_preference


@router.get(
    "/search-request/{search_request_id}",
    response_model=EmailPreferenceResponse,
    summary="Get email preferences by search request",
    description="Get email notification preferences for a specific search request"
)
def get_email_preference_by_search_request(
    search_request_id: int,
    db: Session = Depends(get_db)
):
    """
    Get email preferences for a search request.
    
    Args:
        search_request_id: ID of the search request
        db: Database session
        
    Returns:
        EmailPreferenceResponse: Email preferences
        
    Raises:
        HTTPException 404: If preferences not found
    """
    preference = db.query(EmailPreference).filter(
        EmailPreference.search_request_id == search_request_id
    ).first()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email preferences not found for search request {search_request_id}"
        )
    
    return preference


@router.get(
    "/{preference_id}",
    response_model=EmailPreferenceResponse,
    summary="Get email preferences by ID",
    description="Get email notification preferences by preference ID"
)
def get_email_preference(
    preference_id: int,
    db: Session = Depends(get_db)
):
    """
    Get email preferences by ID.
    
    Args:
        preference_id: ID of the email preference
        db: Database session
        
    Returns:
        EmailPreferenceResponse: Email preferences
        
    Raises:
        HTTPException 404: If preferences not found
    """
    preference = db.query(EmailPreference).filter(
        EmailPreference.id == preference_id
    ).first()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email preferences with id {preference_id} not found"
        )
    
    return preference


@router.get(
    "/",
    response_model=List[EmailPreferenceResponse],
    summary="List all email preferences",
    description="Get a list of all email notification preferences"
)
def list_email_preferences(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all email preferences with pagination.
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List[EmailPreferenceResponse]: List of email preferences
    """
    preferences = db.query(EmailPreference).offset(skip).limit(limit).all()
    return preferences


@router.put(
    "/{preference_id}",
    response_model=EmailPreferenceResponse,
    summary="Update email preferences",
    description="Update email notification preferences"
)
def update_email_preference(
    preference_id: int,
    preference_update: EmailPreferenceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update email preferences.
    
    Args:
        preference_id: ID of the email preference to update
        preference_update: Updated preference data
        db: Database session
        
    Returns:
        EmailPreferenceResponse: Updated email preferences
        
    Raises:
        HTTPException 404: If preferences not found
    """
    # Get existing preference
    db_preference = db.query(EmailPreference).filter(
        EmailPreference.id == preference_id
    ).first()
    
    if not db_preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email preferences with id {preference_id} not found"
        )
    
    # Update fields that were provided
    update_data = preference_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_preference, field, value)
    
    db.commit()
    db.refresh(db_preference)
    
    return db_preference


@router.delete(
    "/{preference_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete email preferences",
    description="Delete email notification preferences"
)
def delete_email_preference(
    preference_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete email preferences.
    
    Args:
        preference_id: ID of the email preference to delete
        db: Database session
        
    Raises:
        HTTPException 404: If preferences not found
    """
    # Get existing preference
    db_preference = db.query(EmailPreference).filter(
        EmailPreference.id == preference_id
    ).first()
    
    if not db_preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email preferences with id {preference_id} not found"
        )
    
    db.delete(db_preference)
    db.commit()
    
    return None