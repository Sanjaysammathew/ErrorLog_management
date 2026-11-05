from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.user import ApprovalStatus
from app.schemas.error_ticketSchema import TicketResponse


class ApprovalDecision(BaseModel):
    """Define the available outcomes for an approval decision.

        These values represent the manager's decision on a request.
    """

    status: ApprovalStatus
    decision_reason: Optional[str] = None


class ApprovalAction(BaseModel):
    """Validate a manager's approval or rejection action.

        The schema may include a reason accompanying the decision.
    """

    decision_reason: Optional[str] = None


class ApprovalResponse(BaseModel):
    """Define the approval details returned by the API.

        The schema presents the request status and decision information.
    """

    id: int
    ticket_id: int
    manager_id: int
    status: ApprovalStatus
    decision_reason: Optional[str] = None
    approved_at: Optional[datetime] = None
    ticket: TicketResponse

    model_config = ConfigDict(from_attributes=True)
