from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketImageResponse(BaseModel):
    """Define the image attachment details returned by the API.

        The schema exposes image metadata associated with a ticket.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    uploaded_by_id: int
    original_filename: str
    file_path: str
    content_type: str
    size_bytes: int
    created_at: datetime
