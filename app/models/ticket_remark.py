from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.error_ticket import ErrorTickets
    from app.models.user import user


class TicketRemark(Base):
    """Represent a remark added to a support ticket.

    The record tracks the remark content, author, and related ticket.
    """

    __tablename__ = "ticket_remarks"
    __table_args__ = (
        Index("ix_ticket_remarks_ticket_id", "ticket_id"),
        Index("ix_ticket_remarks_user_id", "user_id"),
        Index("ix_ticket_remarks_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("error_tickets.id"), nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    remark: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    ticket: Mapped["ErrorTickets"] = relationship(
        "ErrorTickets", back_populates="remarks"
    )

    user: Mapped["user"] = relationship("user", back_populates="remarks")

    @property
    def ticket_number(self) -> str | None:
        """Return the human-readable number for the related ticket.

        This property exposes the ticket identifier through its relationship.
        """
        return self.ticket.ticket_number if self.ticket else None

    @property
    def admin_id(self) -> int:
        """Return the administrator identifier associated with the record.

        This property exposes the related administrator through the model relationship.
        """
        return self.user_id

    @property
    def is_overdue(self) -> bool:
        """Determine whether overdue applies to the current record.

        The result is used by application logic to make a decision.
        """
        if self.ticket is None or self.ticket.due_at is None:
            return False
        if self.ticket.status in {"resolved", "rejected", "closed"}:
            return False
        return datetime.utcnow() > self.ticket.due_at
