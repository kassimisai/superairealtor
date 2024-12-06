import pytest
from fastapi import status
from app.models.user import User
from app.core.security import get_password_hash

def test_register_user(client, db):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "company_name": "Test Company",
        "license_number": "TEST123",
        "role": "agent",
    }

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data

    # Check that user was created in database
    user = db.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.email == user_data["email"]
    assert user.full_name == user_data["full_name"]

def test_register_user_duplicate_email(client, db):
    # Create a user first
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123"),
        role="agent",
    )
    db.add(user)
    db.commit()

    # Try to register with the same email
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Another User",
        "role": "agent",
    }

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]

def test_login_user(client, db):
    # Create a user first
    password = "testpassword123"
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash(password),
        role="agent",
    )
    db.add(user)
    db.commit()

    # Try to login
    response = client.post(
        "/auth/login",
        data={
            "username": user.email,
            "password": password,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_wrong_password(client, db):
    # Create a user first
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123"),
        role="agent",
    )
    db.add(user)
    db.commit()

    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        data={
            "username": user.email,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_user_not_found(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in response.json()["detail"] 