from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.api.dependencies import get_db
from app.models.global_email_preference import GlobalEmailPreference
from app.schemas.global_email_preference import (
    GlobalEmailPreferenceCreate,
    GlobalEmailPreferenceUpdate,
    GlobalEmailPreferenceResponse
)

router = APIRouter(prefix="/global-email-preferences", tags=["Global Email Preferences"])

@router.post("/", response_model=GlobalEmailPreferenceResponse, status_code=201)
def create_or_update_preferences(
    preferences: GlobalEmailPreferenceCreate,
    db: Session = Depends(get_db)
):
    """
    Create or update global email preferences for a user.
    If preferences exist for this email, update them. Otherwise, create new.
    """
    # Check if preferences already exist
    existing = db.query(GlobalEmailPreference).filter(
        GlobalEmailPreference.email_address == preferences.email_address
    ).first()
    
    if existing:
        # Update existing preferences
        for key, value in preferences.model_dump().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new preferences
    db_preference = GlobalEmailPreference(**preferences.model_dump())
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

@router.get("/{email}", response_model=GlobalEmailPreferenceResponse)
def get_preferences(email: str, db: Session = Depends(get_db)):
    """
    Get global email preferences for a specific email address.
    """
    preference = db.query(GlobalEmailPreference).filter(
        GlobalEmailPreference.email_address == email
    ).first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Preferences not found")
    
    return preference

@router.patch("/{email}", response_model=GlobalEmailPreferenceResponse)
def update_preferences(
    email: str,
    updates: GlobalEmailPreferenceUpdate,
    db: Session = Depends(get_db)
):
    """
    Partially update global email preferences.
    Only provided fields will be updated.
    """
    preference = db.query(GlobalEmailPreference).filter(
        GlobalEmailPreference.email_address == email
    ).first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Preferences not found")
    
    # Update only provided fields
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(preference, key, value)
    
    db.commit()
    db.refresh(preference)
    return preference

@router.delete("/{email}", status_code=204)
def delete_preferences(email: str, db: Session = Depends(get_db)):
    """
    Delete global email preferences for a user.
    """
    preference = db.query(GlobalEmailPreference).filter(
        GlobalEmailPreference.email_address == email
    ).first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Preferences not found")
    
    db.delete(preference)
    db.commit()
    return None