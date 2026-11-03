from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class RemarkCreate(BaseModel):
    remark: str = Field(..., min_length=1)


class RemarkResponse(BaseModel):
    id: int
    ticket_id: int
    ticket_number: str | None = None
    user_id: int
    admin_id: int
    remark: str
    is_overdue: bool

    model_config = ConfigDict(from_attributes=True)
