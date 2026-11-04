from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.error_ticket import ErrorTickets
    from app.models.ticket_approval import TicketApproval
    from app.models.ticket_remark import TicketRemark
    from app.models.ticket_status_history import TicketStatusHistory
    from app.models.ticket_remark import TicketRemark
    from app.models.ticket_image import TicketImage


class UserRole(str, PyEnum):
    """Enumeration for user roles."""

    ADMIN = "admin"
    EMPLOYEE = "employee"
    MANAGER = "manager"


class TicketPriority(str, PyEnum):
    """Enumeration for ticket priorities."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ApprovalStatus(str, PyEnum):
    """Enumeration for approval status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class user(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_role", "role"),
        Index("ix_users_is_active", "is_active"),
        Index("ix_users_manager_id", "manager_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.EMPLOYEE,
        server_default="EMPLOYEE",
        nullable=False,
    )
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )

    # Relationships
    manager: Mapped[Optional["user"]] = relationship(
        "user", remote_side=[id], back_populates="subordinates"
    )
    subordinates: Mapped[list["user"]] = relationship(
        "user", back_populates="manager"
    )
    ticket_created: Mapped[list["ErrorTickets"]] = relationship(
        "ErrorTickets",
        foreign_keys="ErrorTickets.user_id",
        back_populates="created_by_user",
    )
    tickets_assigned: Mapped[list["ErrorTickets"]] = relationship(
        "ErrorTickets",
        foreign_keys="ErrorTickets.assigned_admin_id",
        back_populates="assigned_admin",
    )
    approvals_given: Mapped[list["TicketApproval"]] = relationship(
        "TicketApproval", back_populates="manager"
    )
    remarks: Mapped[list["TicketRemark"]] = relationship(
        "TicketRemark", back_populates="user"
    )
    status_history: Mapped[list["TicketStatusHistory"]] = relationship(
        "TicketStatusHistory", back_populates="changed_by"
    )
    ticket_images_uploaded: Mapped[list["TicketImage"]] = relationship(
        "TicketImage", back_populates="uploaded_by"
    )
    remarks: Mapped[list["TicketRemark"]] = relationship(
        "TicketRemark", back_populates="user"
    )
