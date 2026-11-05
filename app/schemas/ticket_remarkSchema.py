from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class RemarkCreate(BaseModel):
    """Validate the content of a new ticket remark.

        The schema contains the information accepted when adding a remark.
    """
    remark: str = Field(..., min_length=1)


class RemarkResponse(BaseModel):
    """Define a ticket remark as returned by the API.

        The schema includes remark content and its associated details.
    """
    id: int
    ticket_id: int
    ticket_number: str | None = None
    user_id: int
    admin_id: int
    remark: str
    is_overdue: bool

    model_config = ConfigDict(from_attributes=True)
