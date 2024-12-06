from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from ..models.lead import LeadStatus, LeadSource

class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: LeadStatus = LeadStatus.NEW
    source: LeadSource = LeadSource.OTHER
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    user_id: UUID

class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

class LeadInDB(LeadBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    last_contacted: Optional[datetime] = None
    metadata: dict = {}

    class Config:
        from_attributes = True

class LeadResponse(LeadInDB):
    pass

class LeadQualification(BaseModel):
    lead_id: UUID
    conversation_history: list[str]
    criteria: dict 