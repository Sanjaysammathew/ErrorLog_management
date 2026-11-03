from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.ErrorCategory import IssueType
from app.models.user import TicketPriority
from app.schemas.error_categorySchema import CategoryResponse
from app.schemas.userSchema import UserResponse


class TicketStatus(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    CLOSED = "closed"


class TicketBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    priority: TicketPriority = TicketPriority.MEDIUM


class TicketCreate(TicketBase):
    issue_type: IssueType


class TicketUpdateStatus(BaseModel):
    status: TicketStatus
    status_change_remark: Optional[str] = None


class TicketResponse(TicketBase):
    id: int
    ticket_number: str
    status: TicketStatus
    user_id: int
    assigned_admin_id: int
    requires_approval: bool
    created_at: datetime
    updated_at: datetime
    due_at: Optional[datetime] = None

    category: Optional[CategoryResponse] = None
    created_by_user: Optional[UserResponse] = None
    assigned_admin: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
