from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.ErrorCategory import ErrorCategory
    from app.models.ticket_approval import TicketApproval
    from app.models.ticket_remark import TicketRemark
    from app.models.ticket_status_history import TicketStatusHistory
    from app.models.ticket_remark import TicketRemark
    from app.models.user import user


class ErrorTickets(Base):
    """ErrorTicket model class."""

    __tablename__ = "error_tickets"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved', 'closed')",
            name="ck_error_tickets_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="ck_error_tickets_priority",
        ),
        Index("ix_error_tickets_category_id", "category_id"),
        Index("ix_error_tickets_user_id", "user_id"),
        Index("ix_error_tickets_status", "status"),
        Index("ix_error_tickets_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="open", server_default="open"
    )
    priority: Mapped[str] = mapped_column(
        String(50), nullable=False, default="medium", server_default="medium"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("error_categories.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    category: Mapped["ErrorCategory"] = relationship(
        "ErrorCategory", back_populates="tickets"
    )
    created_by_user: Mapped["user"] = relationship(
        "user", foreign_keys=[user_id], back_populates="ticket_created"
    )

    approvals: Mapped[list["TicketApproval"]] = relationship(
        "TicketApproval", back_populates="ticket", cascade="all, delete-orphan"
    )

    remarks: Mapped[list["TicketRemark"]] = relationship(
        "TicketRemark", back_populates="ticket", cascade="all, delete-orphan"
    )

    status_history: Mapped[list["TicketStatusHistory"]] = relationship(
        "TicketStatusHistory", back_populates="ticket", cascade="all, delete-orphan"
    )

    remarks: Mapped[list["TicketRemark"]] = relationship(
        "TicketRemark", back_populates="ticket", cascade="all, delete-orphan"
    )
