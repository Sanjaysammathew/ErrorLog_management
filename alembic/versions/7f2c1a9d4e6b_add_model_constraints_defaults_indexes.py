"""add model constraints, defaults, and indexes

Revision ID: 7f2c1a9d4e6b
Revises: b9536c3b6da7
Create Date: 2026-11-03 09:50:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "7f2c1a9d4e6b"
down_revision: str | Sequence[str] | None = "b9536c3b6da7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "role",
        existing_type=sa.Enum("ADMIN", "EMPLOYEE", "MANAGER", name="userrole"),
        server_default="EMPLOYEE",
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "is_active",
        existing_type=sa.Boolean(),
        server_default=sa.text("true"),
        existing_nullable=False,
    )
    op.alter_column(
        "error_categories",
        "default_sla_hours",
        existing_type=sa.Integer(),
        server_default="24",
        existing_nullable=False,
    )
    op.alter_column(
        "error_categories",
        "requires_approval_default",
        existing_type=sa.Boolean(),
        server_default=sa.text("false"),
        existing_nullable=False,
    )
    op.alter_column(
        "error_categories",
        "is_active",
        existing_type=sa.Boolean(),
        server_default=sa.text("true"),
        existing_nullable=False,
    )
    op.alter_column(
        "error_categories",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_nullable=False,
    )
    op.alter_column(
        "error_tickets",
        "status",
        existing_type=sa.String(length=50),
        server_default="open",
        existing_nullable=False,
    )
    op.alter_column(
        "error_tickets",
        "priority",
        existing_type=sa.String(length=50),
        server_default="medium",
        existing_nullable=False,
    )
    op.alter_column(
        "error_tickets",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_nullable=False,
    )
    op.alter_column(
        "error_tickets",
        "updated_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_nullable=False,
    )
    op.alter_column(
        "ticket_approvals",
        "status",
        existing_type=sa.Enum(
            "PENDING", "APPROVED", "REJECTED", name="approvalstatus"
        ),
        server_default="PENDING",
        existing_nullable=False,
    )
    op.alter_column(
        "ticket_remarks",
        "is_internal",
        existing_type=sa.Boolean(),
        server_default=sa.text("false"),
        existing_nullable=False,
    )
    op.alter_column(
        "ticket_remarks",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_nullable=False,
    )
    op.alter_column(
        "ticket_status_history",
        "changed_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_nullable=False,
    )

    op.create_check_constraint(
        "ck_error_categories_sla_positive",
        "error_categories",
        "default_sla_hours > 0",
    )
    op.create_check_constraint(
        "ck_error_tickets_status",
        "error_tickets",
        "status IN ('open', 'in_progress', 'resolved', 'closed')",
    )
    op.create_check_constraint(
        "ck_error_tickets_priority",
        "error_tickets",
        "priority IN ('low', 'medium', 'high')",
    )
    op.create_unique_constraint(
        "uq_ticket_approvals_ticket_manager",
        "ticket_approvals",
        ["ticket_id", "manager_id"],
    )
    op.create_check_constraint(
        "ck_ticket_approvals_decision_timestamp",
        "ticket_approvals",
        "approved_at IS NULL OR status IN ('APPROVED', 'REJECTED')",
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

    for table, name, columns in (
        ("users", "ix_users_role", ["role"]),
        ("users", "ix_users_is_active", ["is_active"]),
        ("users", "ix_users_manager_id", ["manager_id"]),
        ("error_categories", "ix_error_categories_issue_type", ["issue_type"]),
        ("error_categories", "ix_error_categories_is_active", ["is_active"]),
        ("error_tickets", "ix_error_tickets_category_id", ["category_id"]),
        ("error_tickets", "ix_error_tickets_user_id", ["user_id"]),
        ("error_tickets", "ix_error_tickets_status", ["status"]),
        ("error_tickets", "ix_error_tickets_created_at", ["created_at"]),
        ("ticket_approvals", "ix_ticket_approvals_status", ["status"]),
        ("ticket_remarks", "ix_ticket_remarks_ticket_id", ["ticket_id"]),
        ("ticket_remarks", "ix_ticket_remarks_user_id", ["user_id"]),
        ("ticket_remarks", "ix_ticket_remarks_created_at", ["created_at"]),
        ("ticket_status_history", "ix_status_history_ticket_id", ["ticket_id"]),
        ("ticket_status_history", "ix_status_history_changed_by_id", ["changed_by_id"]),
        ("ticket_status_history", "ix_status_history_changed_at", ["changed_at"]),
    ):
        op.create_index(name, table, columns, unique=False)


def downgrade() -> None:
    for table, name in (
        ("ticket_status_history", "ix_status_history_changed_at"),
        ("ticket_status_history", "ix_status_history_changed_by_id"),
        ("ticket_status_history", "ix_status_history_ticket_id"),
        ("ticket_remarks", "ix_ticket_remarks_created_at"),
        ("ticket_remarks", "ix_ticket_remarks_user_id"),
        ("ticket_remarks", "ix_ticket_remarks_ticket_id"),
        ("ticket_approvals", "ix_ticket_approvals_status"),
        ("error_tickets", "ix_error_tickets_created_at"),
        ("error_tickets", "ix_error_tickets_status"),
        ("error_tickets", "ix_error_tickets_user_id"),
        ("error_tickets", "ix_error_tickets_category_id"),
        ("error_categories", "ix_error_categories_is_active"),
        ("error_categories", "ix_error_categories_issue_type"),
        ("users", "ix_users_manager_id"),
        ("users", "ix_users_is_active"),
        ("users", "ix_users_role"),
    ):
        op.drop_index(name, table_name=table)

    op.drop_constraint(
        "ck_status_history_new_status", "ticket_status_history", type_="check"
    )
    op.drop_constraint(
        "ck_status_history_old_status", "ticket_status_history", type_="check"
    )
    op.drop_constraint(
        "ck_ticket_approvals_decision_timestamp",
        "ticket_approvals",
        type_="check",
    )
    op.drop_constraint(
        "uq_ticket_approvals_ticket_manager", "ticket_approvals", type_="unique"
    )
    op.drop_constraint("ck_error_tickets_priority", "error_tickets", type_="check")
    op.drop_constraint("ck_error_tickets_status", "error_tickets", type_="check")
    op.drop_constraint(
        "ck_error_categories_sla_positive", "error_categories", type_="check"
    )

    for table, column, existing_type in (
        ("ticket_status_history", "changed_at", sa.DateTime()),
        ("ticket_remarks", "created_at", sa.DateTime()),
        ("ticket_remarks", "is_internal", sa.Boolean()),
        (
            "ticket_approvals",
            "status",
            sa.Enum("PENDING", "APPROVED", "REJECTED", name="approvalstatus"),
        ),
        ("error_tickets", "updated_at", sa.DateTime()),
        ("error_tickets", "created_at", sa.DateTime()),
        ("error_tickets", "priority", sa.String(length=50)),
        ("error_tickets", "status", sa.String(length=50)),
        ("error_categories", "created_at", sa.DateTime()),
        ("error_categories", "is_active", sa.Boolean()),
        ("error_categories", "requires_approval_default", sa.Boolean()),
        ("error_categories", "default_sla_hours", sa.Integer()),
        ("users", "is_active", sa.Boolean()),
        (
            "users",
            "role",
            sa.Enum("ADMIN", "EMPLOYEE", "MANAGER", name="userrole"),
        ),
        ("users", "created_at", sa.DateTime()),
    ):
        op.alter_column(
            table, column, existing_type=existing_type, server_default=None
        )
