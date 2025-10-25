from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.lead import Lead, LeadStatus
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadInDB, LeadUpdate
from app.api.v1.auth import get_current_active_user
from app.services.email import send_lead_notification
from app.services.file import save_resume

router = APIRouter()
logger = get_logger()

@router.post("/", response_model=LeadInDB)
async def create_lead(
    *,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    _: None = Depends(RateLimiter(times=100, seconds=60))
) -> Lead:
    """
    Create a new lead with resume upload.
    """
    # Save the resume file
    resume_path = await save_resume(resume)
    
    # Create lead in database
    lead = Lead(
        first_name=first_name,
        last_name=last_name,
        email=email,
        resume_path=resume_path,
        status=LeadStatus.PENDING
    )
    try:
        db.add(lead)
        db.commit()
        db.refresh(lead)
        logger.info(f"Created new lead: {lead.email}")
        
        # Send notifications in background
        await send_lead_notification(lead)
        logger.info(f"Queued notification for lead: {lead.email}")
        return lead
    except Exception as e:
        logger.error(f"Error creating lead: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating lead"
        )

@router.get("/", response_model=List[LeadInDB])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Lead]:
    """
    Retrieve leads. Can be filtered by status.
    """
    try:
        query = db.query(Lead)
        if status:
            query = query.filter(Lead.status == status)
        leads = query.offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(leads)} leads with status: {status if status else 'all'}")
        return leads
    except Exception as e:
        logger.error(f"Error retrieving leads: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving leads"
        )

@router.get("/{lead_id}", response_model=LeadInDB)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Lead:
    """
    Get a specific lead by ID.
    """
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            logger.warning(f"Lead not found with ID: {lead_id}")
            raise HTTPException(status_code=404, detail="Lead not found")
        logger.info(f"Retrieved lead: {lead.id} ({lead.email})")
        return lead
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving lead {lead_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving lead"
        )

@router.patch("/{lead_id}/status", response_model=LeadInDB)
async def update_lead_status(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Lead:
    """
    Update a lead's status.
    """
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            logger.warning(f"Lead not found with ID: {lead_id}")
            raise HTTPException(status_code=404, detail="Lead not found")
        
        old_status = lead.status
        lead.status = lead_update.status
        db.add(lead)
        db.commit()
        db.refresh(lead)
        
        logger.info(f"Updated lead {lead.id} status from {old_status} to {lead.status}")
        return lead
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead {lead_id} status: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating lead status"
        )