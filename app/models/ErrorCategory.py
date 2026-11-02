from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.error_ticket import ErrorTickets


class ErrorCategory(Base):
    """ErrorCategory model class."""

    __tablename__ = "error_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    default_sla_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=24)
    requires_approval_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # realtionships
    tickets: Mapped[list["ErrorTickets"]] = relationship(
        "ErrorTickets", back_populates="category"
    )
