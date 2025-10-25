from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from app.core.config import settings
from app.db.session import get_db
from app.models.lead import Lead, LeadStatus
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadInDB, LeadUpdate
from app.api.v1.auth import get_current_active_user
from app.services.email import send_lead_notification
from app.services.file import save_resume

router = APIRouter()

@router.post("/", response_model=LeadInDB)
async def create_lead(
    *,
    db: Session = Depends(get_db),
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
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    # Send notifications
    await send_lead_notification(lead)
    
    return lead

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
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/{lead_id}", response_model=LeadInDB)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Lead:
    """
    Get a specific lead by ID.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

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
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.status = lead_update.status
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    return lead