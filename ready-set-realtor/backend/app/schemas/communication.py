from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from ..models.communication import CommunicationType, CommunicationDirection, CommunicationStatus

class CommunicationBase(BaseModel):
    type: CommunicationType
    direction: CommunicationDirection
    content: Optional[str] = None
    status: CommunicationStatus = CommunicationStatus.SCHEDULED
    scheduled_at: Optional[datetime] = None

class CommunicationCreate(CommunicationBase):
    user_id: UUID
    lead_id: UUID

class CommunicationUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[CommunicationStatus] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    metadata: Optional[dict] = None

class CommunicationInDB(CommunicationBase):
    id: UUID
    user_id: UUID
    lead_id: UUID
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None
    metadata: dict = {}

    class Config:
        from_attributes = True

class CommunicationResponse(CommunicationInDB):
    pass

class EmailCommunication(BaseModel):
    lead_id: UUID
    subject: str
    body: str
    template_name: Optional[str] = None
    cc: Optional[list[str]] = None
    bcc: Optional[list[str]] = None

class SMSCommunication(BaseModel):
    lead_id: UUID
    message: str

class CallCommunication(BaseModel):
    lead_id: UUID
    script: Optional[str] = None
    recording_url: Optional[str] = None 