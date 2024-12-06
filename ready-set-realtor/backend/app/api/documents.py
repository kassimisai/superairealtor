from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..core.database import get_db
from ..core.security import get_current_user, TokenData
from ..schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentGeneration,
    DocumentSignatureRequest,
    DocumentSignatureStatus
)
from ..models.document import Document, DocumentStatus
from ..services.document_service import document_service

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("", response_model=DocumentResponse)
async def create_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Create a new document.
    """
    db_document = Document(**document_data.model_dump())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.get("", response_model=List[DocumentResponse])
async def get_documents(
    lead_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all documents, optionally filtered by lead_id.
    """
    query = db.query(Document).filter(
        Document.user_id == current_user.user_id
    )
    
    if lead_id:
        query = query.filter(Document.lead_id == lead_id)
    
    documents = query.offset(skip).limit(limit).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get a specific document by ID.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.user_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document

@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Update a document's information.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.user_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    for field, value in document_data.model_dump(exclude_unset=True).items():
        setattr(document, field, value)

    db.commit()
    db.refresh(document)
    return document

@router.post("/generate", response_model=DocumentResponse)
async def generate_document(
    generation_data: DocumentGeneration,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Generate a new document from a template.
    """
    # Generate document content
    content = await document_service.generate_document(
        generation_data.template_name,
        generation_data.context
    )

    # Create document record
    document = Document(
        user_id=current_user.user_id,
        lead_id=generation_data.context.get("lead_id"),
        title=f"{generation_data.template_name} - {generation_data.context.get('property_address')}",
        type=generation_data.template_name,
        content=content,
        status=DocumentStatus.DRAFT
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

@router.post("/{document_id}/sign", response_model=DocumentResponse)
async def send_for_signature(
    document_id: UUID,
    signature_request: DocumentSignatureRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Send a document for electronic signature.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.user_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Send document for signature
    envelope_id = await document_service.send_for_signature(
        document.content,
        document.title,
        signature_request.signers
    )

    # Update document status
    document.status = DocumentStatus.PENDING_SIGNATURE
    document.docusign_id = envelope_id
    document.metadata.update({
        "signers": signature_request.signers,
        "sent_for_signature_at": datetime.now().isoformat()
    })

    db.commit()
    db.refresh(document)
    return document

@router.get("/{document_id}/signature-status", response_model=DocumentSignatureStatus)
async def get_signature_status(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get the signature status of a document.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.user_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if not document.docusign_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has not been sent for signature"
        )

    # Get signature status from DocuSign
    status = await document_service.get_signature_status(document.docusign_id)

    return DocumentSignatureStatus(
        document_id=document.id,
        status=status["status"],
        signed_by=status.get("signed_by"),
        signed_at=status.get("completed_datetime")
    ) 