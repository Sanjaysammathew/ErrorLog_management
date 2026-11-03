"""remove remark internal flag

Revision ID: a1b3c5d7e9f2
Revises: 9c6e2a4b8d1f
Create Date: 2026-11-03 16:24:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "a1b3c5d7e9f2"
down_revision: Union[str, Sequence[str], None] = "9c6e2a4b8d1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("ticket_remarks", "is_internal")


def downgrade() -> None:
    import sqlalchemy as sa

    op.add_column(
        "ticket_remarks",
        sa.Column(
            "is_internal",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
