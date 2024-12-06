from sqlalchemy import Column, String, JSON, Enum as SQLEnum
import enum
from .base import BaseModel

class UserRole(str, enum.Enum):
    AGENT = "agent"
    BROKER = "broker"
    ADMIN = "admin"

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    company_name = Column(String)
    license_number = Column(String)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.AGENT)
    settings = Column(JSON, default={}) 