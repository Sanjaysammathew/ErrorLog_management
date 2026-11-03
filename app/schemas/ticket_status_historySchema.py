from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StatusHistoryResponse(BaseModel):
    id: int
    ticket_id: int
    changed_by_id: int
    old_status: str | None = None
    new_status: str
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)
