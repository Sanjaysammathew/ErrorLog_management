"""remove remarks from status history

Revision ID: b2d4f6a8c0e1
Revises: a1b3c5d7e9f2
Create Date: 2026-11-03 16:34:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "b2d4f6a8c0e1"
down_revision: Union[str, Sequence[str], None] = "a1b3c5d7e9f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("ticket_status_history", "remarks")


def downgrade() -> None:
    import sqlalchemy as sa

    op.add_column(
        "ticket_status_history",
        sa.Column("remarks", sa.Text(), nullable=True),
    )
