import pytest
from fastapi import status
from datetime import datetime
from app.models.communication import Communication, CommunicationType, CommunicationDirection, CommunicationStatus
from app.models.user import User
from app.models.lead import Lead
from app.core.security import get_password_hash

@pytest.fixture
def test_lead(db, test_user):
    user = User(
        id=test_user["id"],
        email=test_user["email"],
        full_name=test_user["full_name"],
        hashed_password=get_password_hash("testpassword123"),
        role=test_user["role"],
    )
    db.add(user)
    
    lead = Lead(
        user_id=user.id,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+1234567890",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

def test_send_email(authorized_client, db, test_lead):
    email_data = {
        "lead_id": str(test_lead.id),
        "to_email": test_lead.email,
        "subject": "Test Email",
        "body": "This is a test email",
    }

    response = authorized_client.post("/communications/email", json=email_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["type"] == CommunicationType.EMAIL.value
    assert data["direction"] == CommunicationDirection.OUTBOUND.value
    assert data["status"] == CommunicationStatus.SENT.value
    assert data["content"] == email_data["body"]

def test_send_sms(authorized_client, db, test_lead):
    sms_data = {
        "lead_id": str(test_lead.id),
        "to_number": test_lead.phone,
        "message": "This is a test SMS",
    }

    response = authorized_client.post("/communications/sms", json=sms_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["type"] == CommunicationType.SMS.value
    assert data["direction"] == CommunicationDirection.OUTBOUND.value
    assert data["status"] == CommunicationStatus.SENT.value
    assert data["content"] == sms_data["message"]

def test_make_call(authorized_client, db, test_lead):
    call_data = {
        "lead_id": str(test_lead.id),
        "phone_number": test_lead.phone,
        "assistant_id": "test_assistant_id",
        "script": "This is a test call script",
    }

    response = authorized_client.post("/communications/call", json=call_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["type"] == CommunicationType.CALL.value
    assert data["direction"] == CommunicationDirection.OUTBOUND.value
    assert data["status"] == CommunicationStatus.IN_PROGRESS.value
    assert data["content"] == call_data["script"]

def test_get_communications(authorized_client, db, test_lead, test_user):
    # Create some test communications
    communications = [
        Communication(
            user_id=test_user["id"],
            lead_id=test_lead.id,
            type=CommunicationType.EMAIL,
            direction=CommunicationDirection.OUTBOUND,
            content="Test email",
            status=CommunicationStatus.SENT,
            sent_at=datetime.utcnow(),
        ),
        Communication(
            user_id=test_user["id"],
            lead_id=test_lead.id,
            type=CommunicationType.SMS,
            direction=CommunicationDirection.OUTBOUND,
            content="Test SMS",
            status=CommunicationStatus.SENT,
            sent_at=datetime.utcnow(),
        ),
    ]
    db.add_all(communications)
    db.commit()

    response = authorized_client.get("/communications")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["type"] == CommunicationType.EMAIL.value
    assert data[1]["type"] == CommunicationType.SMS.value

def test_get_call_transcript(authorized_client):
    call_id = "test_call_id"
    response = authorized_client.get(f"/communications/call/{call_id}/transcript")
    assert response.status_code == status.HTTP_200_OK

def test_get_call_recording(authorized_client):
    call_id = "test_call_id"
    response = authorized_client.get(f"/communications/call/{call_id}/recording")
    assert response.status_code == status.HTTP_200_OK 