from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base model for user data."""

    username: str
    email: EmailStr
    department: Optional[str] = None
    role: UserRole = UserRole.EMPLOYEE


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    manager_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    manager_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
