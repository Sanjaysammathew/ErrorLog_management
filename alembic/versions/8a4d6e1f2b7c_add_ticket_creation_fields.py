"""add ticket creation fields

Revision ID: 8a4d6e1f2b7c
Revises: 7f2c1a9d4e6b
Create Date: 2026-11-03 10:50:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "8a4d6e1f2b7c"
down_revision: str | Sequence[str] | None = "7f2c1a9d4e6b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "error_tickets",
        sa.Column("ticket_number", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "error_tickets",
        sa.Column(
            "requires_approval",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.add_column(
        "error_tickets",
        sa.Column("due_at", sa.DateTime(), nullable=True),
    )
    op.create_unique_constraint(
        "uq_error_tickets_ticket_number", "error_tickets", ["ticket_number"]
    )
    op.alter_column(
        "error_tickets",
        "requires_approval",
        server_default=None,
        existing_type=sa.Boolean(),
        existing_nullable=False,
    )
    op.drop_constraint("ck_error_tickets_status", "error_tickets", type_="check")
    op.create_check_constraint(
        "ck_error_tickets_status",
        "error_tickets",
        "status IN "
        "('pending_approval', 'open', 'in_progress', 'resolved', 'closed')",
    )
    op.drop_constraint(
        "ck_status_history_old_status", "ticket_status_history", type_="check"
    )
    op.drop_constraint(
        "ck_status_history_new_status", "ticket_status_history", type_="check"
    )
    op.create_check_constraint(
        "ck_status_history_old_status",
        "ticket_status_history",
        "old_status IS NULL OR old_status IN "
        "('pending_approval', 'open', 'in_progress', 'resolved', 'closed')",
    )
    op.create_check_constraint(
        "ck_status_history_new_status",
        "ticket_status_history",
        "new_status IN "
        "('pending_approval', 'open', 'in_progress', 'resolved', 'closed')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_status_history_new_status", "ticket_status_history", type_="check"
    )
    op.drop_constraint(
        "ck_status_history_old_status", "ticket_status_history", type_="check"
    )
    op.create_check_constraint(
        "ck_status_history_old_status",
        "ticket_status_history",
        "old_status IS NULL OR old_status IN "
        "('open', 'in_progress', 'resolved', 'closed')",
    )
    op.create_check_constraint(
        "ck_status_history_new_status",
        "ticket_status_history",
        "new_status IN ('open', 'in_progress', 'resolved', 'closed')",
    )
    op.drop_constraint("ck_error_tickets_status", "error_tickets", type_="check")
    op.create_check_constraint(
        "ck_error_tickets_status",
        "error_tickets",
        "status IN ('open', 'in_progress', 'resolved', 'closed')",
    )
    op.drop_constraint(
        "uq_error_tickets_ticket_number", "error_tickets", type_="unique"
    )
    op.drop_column("error_tickets", "due_at")
    op.drop_column("error_tickets", "requires_approval")
    op.drop_column("error_tickets", "ticket_number")
