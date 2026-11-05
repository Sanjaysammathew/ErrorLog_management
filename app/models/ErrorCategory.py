from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.error_ticket import ErrorTickets


class IssueType(str, PyEnum):
    """Define the supported types of reported issues.

        These values are used to classify ticket categories and requests.
    """
    HARDWARE = "HARDWARE"
    SOFTWARE = "SOFTWARE"
    NETWORK = "NETWORK"


class ErrorCategory(Base):
    """ErrorCategory model class."""

    __tablename__ = "error_categories"
    __table_args__ = (
        CheckConstraint(
            "default_sla_hours > 0", name="ck_error_categories_sla_positive"
        ),
        Index("ix_error_categories_issue_type", "issue_type"),
        Index("ix_error_categories_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    issue_type: Mapped[IssueType] = mapped_column(
        Enum(IssueType), nullable=False
    )
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    default_sla_hours: Mapped[int] = mapped_column(
        Integer, nullable=False, default=24, server_default="24"
    )
    requires_approval_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False
    )

    # realtionships
    tickets: Mapped[list["ErrorTickets"]] = relationship(
        "ErrorTickets", back_populates="category"
    )
