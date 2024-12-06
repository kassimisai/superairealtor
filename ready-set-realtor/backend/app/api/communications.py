from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.communication import Communication, CommunicationType, CommunicationDirection, CommunicationStatus
from ..schemas.communication import (
    CommunicationCreate,
    CommunicationUpdate,
    CommunicationResponse,
    EmailCommunication,
    SMSCommunication,
    CallCommunication,
)
from ..services.email_service import email_service
from ..services.twilio_service import twilio_service
from ..services.vapi_service import vapi_service

router = APIRouter(prefix="/communications", tags=["communications"])

@router.get("/", response_model=List[CommunicationResponse])
async def get_communications(
    skip: int = 0,
    limit: int = 100,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all communications for the current user.
    """
    communications = (
        db.query(Communication)
        .filter(Communication.user_id == user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return communications

@router.get("/{communication_id}", response_model=CommunicationResponse)
async def get_communication(
    communication_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific communication by ID.
    """
    communication = (
        db.query(Communication)
        .filter(
            Communication.id == communication_id,
            Communication.user_id == user.id,
        )
        .first()
    )
    if not communication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Communication not found",
        )
    return communication

@router.post("/email", response_model=CommunicationResponse)
async def send_email(
    email_data: EmailCommunication,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send an email communication.
    """
    try:
        # Send email using the email service
        email_result = await email_service.send_email(
            to_email=email_data.to_email,
            subject=email_data.subject,
            body=email_data.body,
            template_name=email_data.template_name,
            cc=email_data.cc,
            bcc=email_data.bcc,
        )

        # Create communication record
        communication = Communication(
            user_id=user.id,
            lead_id=email_data.lead_id,
            type=CommunicationType.EMAIL,
            direction=CommunicationDirection.OUTBOUND,
            content=email_data.body,
            status=CommunicationStatus.SENT,
            sent_at=datetime.utcnow(),
            metadata={"email_id": email_result["id"]},
        )
        db.add(communication)
        db.commit()
        db.refresh(communication)
        return communication
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.post("/sms", response_model=CommunicationResponse)
async def send_sms(
    sms_data: SMSCommunication,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send an SMS communication.
    """
    try:
        # Send SMS using the Twilio service
        sms_result = await twilio_service.send_sms(
            to_number=sms_data.to_number,
            message=sms_data.message,
        )

        # Create communication record
        communication = Communication(
            user_id=user.id,
            lead_id=sms_data.lead_id,
            type=CommunicationType.SMS,
            direction=CommunicationDirection.OUTBOUND,
            content=sms_data.message,
            status=CommunicationStatus.SENT,
            sent_at=datetime.utcnow(),
            metadata={"message_id": sms_result["id"]},
        )
        db.add(communication)
        db.commit()
        db.refresh(communication)
        return communication
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.post("/call", response_model=CommunicationResponse)
async def make_call(
    call_data: CallCommunication,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Make a voice call using Vapi.ai.
    """
    try:
        # Create call using the Vapi service
        call_result = await vapi_service.create_call(
            phone_number=call_data.phone_number,
            assistant_id=call_data.assistant_id,
            initial_message=call_data.script or "Hello, this is Ready Set Realtor calling.",
            metadata={"lead_id": str(call_data.lead_id)},
        )

        # Create communication record
        communication = Communication(
            user_id=user.id,
            lead_id=call_data.lead_id,
            type=CommunicationType.CALL,
            direction=CommunicationDirection.OUTBOUND,
            content=call_data.script,
            status=CommunicationStatus.IN_PROGRESS,
            metadata={"call_id": call_result["id"]},
        )
        db.add(communication)
        db.commit()
        db.refresh(communication)
        return communication
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.get("/call/{call_id}/transcript")
async def get_call_transcript(
    call_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the transcript of a call.
    """
    try:
        # Get transcript using the Vapi service
        transcript = await vapi_service.get_call_transcript(call_id)
        return transcript
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.get("/call/{call_id}/recording")
async def get_call_recording(
    call_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the recording URL of a call.
    """
    try:
        # Get recording using the Vapi service
        recording = await vapi_service.get_call_recording(call_id)
        return recording
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) 