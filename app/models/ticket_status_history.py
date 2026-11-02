from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
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
    __tablename__ = "ticket_status_history"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("error_tickets.id"), nullable=False
    )

    changed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    old_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    new_status: Mapped[str] = mapped_column(String(30), nullable=False)

    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    changed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    ticket: Mapped["ErrorTickets"] = relationship(
        "ErrorTickets", back_populates="status_history"
    )

    changed_by: Mapped["user"] = relationship(
        "user", back_populates="status_history"
    )
