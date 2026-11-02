from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.userSchema import UserResponse


class RemarkCreate(BaseModel):
    remark: str = Field(..., min_length=1)
    is_internal: bool = False


class RemarkResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    remark: str
    is_internal: bool
    created_at: datetime

    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
