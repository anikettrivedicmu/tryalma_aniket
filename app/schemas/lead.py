from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, constr

from app.models.lead import LeadStatus


class LeadBase(BaseModel):
    first_name: constr(min_length=1, max_length=100)
    last_name: constr(min_length=1, max_length=100)
    email: EmailStr


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    status: LeadStatus


class LeadInDB(LeadBase):
    id: int
    resume_path: str
    status: LeadStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True