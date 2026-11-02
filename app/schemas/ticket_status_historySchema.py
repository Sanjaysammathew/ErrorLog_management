from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class StatusHistoryResponse(BaseModel):
    id: int
    ticket_id: int
    old_status: Optional[str] = None
    new_status: str
    changed_by_id: int
    remarks: Optional[str] = None
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)
