from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import TicketPriority
from app.schemas.error_categorySchema import CategoryResponse
from app.schemas.userSchema import UserResponse


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str
    asset_tag: Optional[str] = None
    category_id: int
    priority: TicketPriority = TicketPriority.MEDIUM


class TicketCreate(TicketBase):
    pass


class TicketUpdateStatus(BaseModel):
    status: TicketStatus
    assigned_admin_id: Optional[int] = None
    status_change_remark: Optional[str] = None


class TicketResponse(TicketBase):
    id: int
    ticket_code: str
    employee_id: int
    assigned_admin_id: Optional[int] = None
    status: TicketStatus
    requires_approval: bool
    created_at: datetime
    due_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    employee: Optional[UserResponse] = None
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)
