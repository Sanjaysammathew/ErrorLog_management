from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.user import ApprovalStatus


class ApprovalDecision(BaseModel):
    status: ApprovalStatus
    decision_reason: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: int
    ticket_id: int
    manager_id: int
    status: ApprovalStatus
    decision_reason: Optional[str] = None
    approved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
