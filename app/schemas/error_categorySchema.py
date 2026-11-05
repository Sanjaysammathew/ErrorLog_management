from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ErrorCategory import IssueType


class CategoryBase(BaseModel):
    """Define the shared fields for ticket category data.

        Create, update, and response schemas build on this common shape.
    """

    name: str = Field(..., min_length=2, max_length=100)
    issue_type: IssueType
    description: str | None = None
    default_sla_hours: int = Field(default=24, ge=1)
    requires_approval_default: bool = False


class CategoryCreate(CategoryBase):
    """Validate data used to create a ticket category.

        The schema contains the fields accepted for a new category.
    """

    pass


class CategoryUpdate(BaseModel):
    """Validate data used to update a ticket category.

        The schema contains the editable category fields.
    """

    name: str | None = None
    description: str | None = None
    default_sla_hours: int | None = None
    requires_approval_default: bool | None = None


class CategoryResponse(CategoryBase):
    """Define the category data returned by the API.

        The schema provides a consistent representation to clients.
    """

    id: int
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
