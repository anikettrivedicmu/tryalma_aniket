from enum import Enum
from sqlalchemy import Column, String, Enum as SQLAEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class LeadStatus(str, Enum):
    PENDING = "PENDING"
    REACHED_OUT = "REACHED_OUT"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    resume_path = Column(String(255), nullable=False)
    status = Column(SQLAEnum(LeadStatus), default=LeadStatus.PENDING)
    
    # Audit fields from Base class:
    # created_at
    # updated_at