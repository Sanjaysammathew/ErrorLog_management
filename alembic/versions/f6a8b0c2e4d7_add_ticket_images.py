"""add ticket images

Revision ID: f6a8b0c2e4d7
Revises: e5f7a9b1c3d6
Create Date: 2026-11-04 12:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6a8b0c2e4d7"
down_revision: Union[str, Sequence[str], None] = "e5f7a9b1c3d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ticket_images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_id", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ticket_id"], ["error_tickets.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_path"),
    )
    op.create_index("ix_ticket_images_ticket_id", "ticket_images", ["ticket_id"])
    op.create_index(
        "ix_ticket_images_uploaded_by_id",
        "ticket_images",
        ["uploaded_by_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ticket_images_uploaded_by_id", table_name="ticket_images"
    )
    op.drop_index("ix_ticket_images_ticket_id", table_name="ticket_images")
    op.drop_table("ticket_images")
