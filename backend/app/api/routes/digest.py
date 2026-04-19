"""
Daily Digest API Routes

Endpoints for managing and triggering daily digest emails.
"""

import logging
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.email_service import EmailService
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/digest", tags=["digest"])


@router.post(
    "/send-now",
    summary="Manually trigger daily digest",
    description="Send daily digest emails immediately (for testing)"
)
async def send_digest_now(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger the daily digest email send.
    
    Useful for:
    - Testing the digest functionality
    - Sending digest at non-scheduled times
    - Debugging email issues
    
    Returns:
        dict: Status message
    """
    email_service = EmailService(settings)
    
    # Run in background to not block the response
    background_tasks.add_task(
        send_digest_task,
        email_service,
        db
    )
    
    return {
        "status": "success",
        "message": "Daily digest is being sent in the background"
    }


async def send_digest_task(email_service: EmailService, db: Session):
    """Background task to send digest"""
    try:
        # Prepare digest data
        digest_data = await email_service.prepare_daily_digest_data(db)
        
        # Send to each email
        for email, matches in digest_data.items():
            await email_service.send_daily_digest(
                email=email,
                matches=matches
            )
        
        logger.info(f"Manual digest sent to {len(digest_data)} recipients")
        
    except Exception as e:
        logger.error(f"Manual digest failed: {str(e)}")


@router.get(
    "/preview",
    summary="Preview digest data",
    description="See what would be included in the next digest"
)
async def preview_digest(db: Session = Depends(get_db)):
    """
    Preview the data that would be included in the daily digest.
    
    Useful for:
    - Checking if there are matches to send
    - Debugging digest logic
    - Verifying email preferences
    
    Returns:
        dict: Preview of digest data
    """
    email_service = EmailService(settings)
    digest_data = await email_service.prepare_daily_digest_data(db)
    
    # Format for preview
    preview = {
        "total_recipients": len(digest_data),
        "recipients": []
    }
    
    for email, matches in digest_data.items():
        preview["recipients"].append({
            "email": email,
            "match_count": len(matches),
            "matches": [
                {
                    "product_title": m['product'].title,
                    "product_price": m['product'].price,
                    "search_query": m['search_request'].query
                }
                for m in matches[:5]  # Show first 5 matches
            ]
        })
    
    return preview