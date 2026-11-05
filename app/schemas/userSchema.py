from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base model for user data."""

    username: str
    email: EmailStr
    department: str | None = None
    role: UserRole = UserRole.EMPLOYEE


class UserCreate(UserBase):
    """Validate the details required to create a user account.

        The schema contains the account fields accepted from administrators.
    """
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """Validate editable user account changes.

        The schema contains the account fields that administrators may update.
    """
    username: str | None = None
    email: EmailStr | None = None
    department: str | None = None
    password: str | None = Field(default=None, min_length=6)


class UserResponse(UserBase):
    """Define the user account details returned by the API.

        The schema provides a consistent public representation of a user.
    """
    id: int
    manager_id: int | None = None
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Define a paginated list of users returned by the API.

        The schema combines user records with pagination information.
    """
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
