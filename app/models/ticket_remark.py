from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.error_ticket import ErrorTickets
    from app.models.user import user


class TicketRemark(Base):
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

    is_internal: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )

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
