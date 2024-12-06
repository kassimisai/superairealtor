from sqlalchemy import Column, String, ForeignKey, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import enum
from .base import BaseModel

class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    APPOINTMENT_SET = "appointment_set"
    NEGOTIATING = "negotiating"
    CLOSED = "closed"
    LOST = "lost"

class LeadSource(str, enum.Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    ZILLOW = "zillow"
    REALTOR = "realtor"
    COLD_CALL = "cold_call"
    OTHER = "other"

class Lead(BaseModel):
    __tablename__ = "leads"

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    status = Column(SQLEnum(LeadStatus), nullable=False, default=LeadStatus.NEW)
    source = Column(SQLEnum(LeadSource), nullable=False, default=LeadSource.OTHER)
    last_contacted = Column(DateTime(timezone=True))
    notes = Column(String)
    metadata = Column(JSON, default={}) 