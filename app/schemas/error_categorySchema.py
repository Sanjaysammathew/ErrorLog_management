from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.ErrorCategory import IssueType


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    issue_type: IssueType
    description: Optional[str] = None
    default_sla_hours: int = Field(default=24, ge=1)
    requires_approval_default: bool = False


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    default_sla_hours: Optional[int] = None
    requires_approval_default: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
