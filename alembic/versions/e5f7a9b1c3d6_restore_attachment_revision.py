"""restore the previously published attachment revision

Revision ID: e5f7a9b1c3d6
Revises: d4f6a8b0c2e5
Create Date: 2026-11-04 12:45:00.000000

This compatibility revision is intentionally empty. It restores the revision
identifier used by databases that saw the earlier attachment migration.
"""
from typing import Sequence, Union


revision: str = "e5f7a9b1c3d6"
down_revision: Union[str, Sequence[str], None] = "d4f6a8b0c2e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
