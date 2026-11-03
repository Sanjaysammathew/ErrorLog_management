"""add assigned admin to tickets

Revision ID: 9c6e2a4b8d1f
Revises: 8a4d6e1f2b7c
Create Date: 2026-11-03 15:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c6e2a4b8d1f"
down_revision: Union[str, Sequence[str], None] = "8a4d6e1f2b7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "error_tickets",
        sa.Column(
            "assigned_admin_id",
            sa.Integer(),
            server_default="1",
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_error_tickets_assigned_admin_id_users",
        "error_tickets",
        "users",
        ["assigned_admin_id"],
        ["id"],
    )
    op.create_index(
        "ix_error_tickets_assigned_admin_id",
        "error_tickets",
        ["assigned_admin_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_error_tickets_assigned_admin_id", table_name="error_tickets"
    )
    op.drop_constraint(
        "fk_error_tickets_assigned_admin_id_users",
        "error_tickets",
        type_="foreignkey",
    )
    op.drop_column("error_tickets", "assigned_admin_id")
