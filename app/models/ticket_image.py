from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.error_ticket import ErrorTickets
    from app.models.user import user


class TicketImage(Base):
    __tablename__ = "ticket_images"
    __table_args__ = (
        Index("ix_ticket_images_ticket_id", "ticket_id"),
        Index("ix_ticket_images_uploaded_by_id", "uploaded_by_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("error_tickets.id", ondelete="CASCADE"), nullable=False
    )
    uploaded_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    ticket: Mapped["ErrorTickets"] = relationship(
        "ErrorTickets", back_populates="images"
    )
    uploaded_by: Mapped["user"] = relationship(
        "user", back_populates="ticket_images_uploaded"
    )
