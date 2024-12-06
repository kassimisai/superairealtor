from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime
from ..models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    company_name: Optional[str] = None
    license_number: Optional[str] = None
    role: UserRole = UserRole.AGENT

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    license_number: Optional[str] = None
    settings: Optional[dict] = None

class UserInDB(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    settings: dict = {}

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    pass

class UserLogin(BaseModel):
    email: EmailStr
    password: str 