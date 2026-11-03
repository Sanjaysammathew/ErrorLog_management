"""add rejected ticket status

Revision ID: d4f6a8b0c2e5
Revises: c3e5a7b9d1f4
Create Date: 2026-11-03 19:55:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "d4f6a8b0c2e5"
down_revision: Union[str, Sequence[str], None] = "c3e5a7b9d1f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_error_tickets_status", "error_tickets", type_="check")
    op.create_check_constraint(
        "ck_error_tickets_status",
        "error_tickets",
        "status IN "
        "('pending_approval', 'open', 'in_progress', 'resolved', "
        "'rejected', 'closed')",
    )
    op.drop_constraint(
        "ck_status_history_old_status", "ticket_status_history", type_="check"
    )
    op.create_check_constraint(
        "ck_status_history_old_status",
        "ticket_status_history",
        "old_status IS NULL OR old_status IN "
        "('pending_approval', 'open', 'in_progress', 'resolved', "
        "'rejected', 'closed')",
    )
    op.drop_constraint(
        "ck_status_history_new_status", "ticket_status_history", type_="check"
    )
    op.create_check_constraint(
        "ck_status_history_new_status",
        "ticket_status_history",
        "new_status IN "
        "('pending_approval', 'open', 'in_progress', 'resolved', "
        "'rejected', 'closed')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_error_tickets_status", "error_tickets", type_="check")
    op.create_check_constraint(
        "ck_error_tickets_status",
        "error_tickets",
        "status IN ('pending_approval', 'open', 'in_progress', 'resolved', 'closed')",
    )
    op.drop_constraint(
        "ck_status_history_old_status", "ticket_status_history", type_="check"
    )
    op.create_check_constraint(
        "ck_status_history_old_status",
        "ticket_status_history",
        "old_status IS NULL OR old_status IN "
        "('pending_approval', 'open', 'in_progress', 'resolved', 'closed')",
    )
    op.drop_constraint(
        "ck_status_history_new_status", "ticket_status_history", type_="check"
    )
    op.create_check_constraint(
        "ck_status_history_new_status",
        "ticket_status_history",
        "new_status IN ('pending_approval', 'open', 'in_progress', 'resolved', 'closed')",
    )
