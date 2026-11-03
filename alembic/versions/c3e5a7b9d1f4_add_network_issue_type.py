"""add network issue type

Revision ID: c3e5a7b9d1f4
Revises: b2d4f6a8c0e1
Create Date: 2026-11-03 17:33:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "c3e5a7b9d1f4"
down_revision: Union[str, Sequence[str], None] = "b2d4f6a8c0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE issuetype ADD VALUE IF NOT EXISTS 'NETWORK'")


def downgrade() -> None:
    pass
