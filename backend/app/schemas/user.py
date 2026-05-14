import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True
    role: UserRole = UserRole.OFFICER
    alert_threshold: int = 70
    email_alerts: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr  = None
    name: str  = None
    password: str  = None
    role: UserRole  = None
    alert_threshold: int  = None
    email_alerts: bool  = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UserInDB(UserResponse):
    password_hash: str
