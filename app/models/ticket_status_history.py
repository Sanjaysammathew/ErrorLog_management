from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.error_ticket import ErrorTickets
    from app.models.user import user


class TicketStatusHistory(Base):
    """Represent a recorded status change for a ticket.

        The record preserves the transition and its associated details.
    """
    __tablename__ = "ticket_status_history"
    __table_args__ = (
        CheckConstraint(
            "old_status IS NULL OR old_status IN "
            "('pending_approval', 'open', 'in_progress', 'resolved', "
            "'rejected', 'closed')",
            name="ck_status_history_old_status",
        ),
        CheckConstraint(
            "new_status IN "
            "('pending_approval', 'open', 'in_progress', 'resolved', "
            "'rejected', 'closed')",
            name="ck_status_history_new_status",
        ),
        Index("ix_status_history_ticket_id", "ticket_id"),
        Index("ix_status_history_changed_by_id", "changed_by_id"),
        Index("ix_status_history_changed_at", "changed_at"),
    )

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("error_tickets.id"), nullable=False
    )

    changed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    old_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    new_status: Mapped[str] = mapped_column(String(30), nullable=False)

    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    ticket: Mapped["ErrorTickets"] = relationship(
        "ErrorTickets", back_populates="status_history"
    )

    changed_by: Mapped["user"] = relationship(
        "user", back_populates="status_history"
    )
