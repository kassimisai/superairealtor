from sqlalchemy import Column, String, ForeignKey, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import enum
from .base import BaseModel

class CommunicationType(str, enum.Enum):
    CALL = "call"
    EMAIL = "email"
    TEXT = "text"
    MEETING = "meeting"

class CommunicationDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class CommunicationStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Communication(BaseModel):
    __tablename__ = "communications"

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'), nullable=False)
    type = Column(SQLEnum(CommunicationType), nullable=False)
    direction = Column(SQLEnum(CommunicationDirection), nullable=False)
    content = Column(String)
    status = Column(SQLEnum(CommunicationStatus), nullable=False, default=CommunicationStatus.SCHEDULED)
    scheduled_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    metadata = Column(JSON, default={}) 