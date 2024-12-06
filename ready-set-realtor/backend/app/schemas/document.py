from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from ..models.document import DocumentType, DocumentStatus

class DocumentBase(BaseModel):
    title: str
    type: DocumentType
    status: DocumentStatus = DocumentStatus.DRAFT

class DocumentCreate(DocumentBase):
    user_id: UUID
    lead_id: UUID
    content: str

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None
    docusign_id: Optional[str] = None
    storage_path: Optional[str] = None
    metadata: Optional[dict] = None

class DocumentInDB(DocumentBase):
    id: UUID
    user_id: UUID
    lead_id: UUID
    created_at: datetime
    updated_at: datetime
    docusign_id: Optional[str] = None
    storage_path: Optional[str] = None
    metadata: dict = {}

    class Config:
        from_attributes = True

class DocumentResponse(DocumentInDB):
    pass

class DocumentGeneration(BaseModel):
    template_name: str
    context: dict

class DocumentSignatureRequest(BaseModel):
    document_id: UUID
    signers: List[dict]  # List of {name: str, email: str} dictionaries

class DocumentSignatureStatus(BaseModel):
    document_id: UUID
    status: DocumentStatus
    signed_by: Optional[List[str]] = None
    signed_at: Optional[datetime] = None 