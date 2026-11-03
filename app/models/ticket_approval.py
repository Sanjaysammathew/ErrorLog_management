from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.user import ApprovalStatus

if TYPE_CHECKING:
    from app.models.error_ticket import ErrorTickets
    from app.models.user import user


class TicketApproval(Base):
    __tablename__ = "ticket_approvals"
    __table_args__ = (
        UniqueConstraint(
            "ticket_id", "manager_id", name="uq_ticket_approvals_ticket_manager"
        ),
        CheckConstraint(
            "approved_at IS NULL OR status IN ('APPROVED', 'REJECTED')",
            name="ck_ticket_approvals_decision_timestamp",
        ),
        Index("ix_ticket_approvals_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("error_tickets.id"), nullable=False
    )

    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus),
        default=ApprovalStatus.PENDING,
        server_default="PENDING",
        nullable=False,
    )

    decision_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, default=None
    )

    ticket: Mapped["ErrorTickets"] = relationship(
        "ErrorTickets", back_populates="approvals"
    )

    manager: Mapped["user"] = relationship(
        "user", back_populates="approvals_given"
    )
