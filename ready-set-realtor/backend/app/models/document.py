from sqlalchemy import Column, String, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import enum
from .base import BaseModel

class DocumentType(str, enum.Enum):
    PURCHASE_AGREEMENT = "purchase_agreement"
    LISTING_AGREEMENT = "listing_agreement"
    DISCLOSURE = "disclosure"
    AMENDMENT = "amendment"
    ADDENDUM = "addendum"
    OTHER = "other"

class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    SIGNED = "signed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class Document(BaseModel):
    __tablename__ = "documents"

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'), nullable=False)
    title = Column(String, nullable=False)
    type = Column(SQLEnum(DocumentType), nullable=False)
    status = Column(SQLEnum(DocumentStatus), nullable=False, default=DocumentStatus.DRAFT)
    docusign_id = Column(String)
    storage_path = Column(String)
    metadata = Column(JSON, default={}) 