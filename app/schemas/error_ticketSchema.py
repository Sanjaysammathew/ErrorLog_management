from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models.ErrorCategory import IssueType
from app.models.user import TicketPriority
from app.schemas.error_categorySchema import CategoryResponse
from app.schemas.userSchema import UserResponse


class TicketStatus(str, Enum):
    """Define the supported states of a support ticket.

        These values describe a ticket's progress through its workflow.
    """
    PENDING_APPROVAL = "pending_approval"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    CLOSED = "closed"


class TicketStatusUpdate(str, Enum):
    """Represent a validated ticket status transition.

        The schema captures the target state and any transition details.
    """
    PENDING_APPROVAL = "pending_approval"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class TicketBase(BaseModel):
    """Define fields shared by ticket creation and response data.

        Specialized ticket schemas extend this common representation.
    """
    title: str = Field(..., min_length=3, max_length=100)
    description: str | None = None
    priority: TicketPriority = TicketPriority.MEDIUM


class TicketCreate(TicketBase):
    """Validate the information supplied when opening a ticket.

        The schema contains the issue details accepted from a client.
    """
    issue_type: IssueType


class TicketUpdateStatus(BaseModel):
    """Validate a request to change a ticket's status.

        The schema includes the new state and an optional status remark.
    """
    status: TicketStatusUpdate
    status_change_remark: str | None = None


class TicketResponse(TicketBase):
    """Define the ticket information returned by the API.

        The schema presents ticket details in a consistent response shape.
    """
    id: int
    ticket_number: str
    status: TicketStatus
    user_id: int
    assigned_admin_id: int
    requires_approval: bool
    created_at: datetime
    updated_at: datetime
    due_at: datetime | None = None

    category: CategoryResponse | None = None
    created_by_user: UserResponse | None = None
    assigned_admin: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)
