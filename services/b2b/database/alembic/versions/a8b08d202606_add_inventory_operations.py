"""add inventory operations

Revision ID: a8b08d202606
Revises: 7bea7d8e6d06
Create Date: 2026-06-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a8b08d202606"
down_revision: Union[str, Sequence[str], None] = "7bea7d8e6d06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.create_check_constraint(
		"chk_reserved_quantity_positive",
		"skus",
		"reserved_quantity >= 0",
		schema="catalog",
	)
	op.create_table(
		"inventory_operations",
		sa.Column(
			"id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
		),
		sa.Column("operation", sa.String(length=32), nullable=False),
		sa.Column("idempotency_key", sa.UUID(), nullable=False),
		sa.Column("items", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
		sa.Column(
			"created_at",
			sa.DateTime(timezone=True),
			server_default=sa.text("now()"),
			nullable=False,
		),
		sa.PrimaryKeyConstraint("id"),
		sa.UniqueConstraint(
			"operation",
			"idempotency_key",
			name="uq_inventory_operation_idempotency",
		),
		schema="catalog",
	)


def downgrade() -> None:
	op.drop_table("inventory_operations", schema="catalog")
	op.drop_constraint(
		"chk_reserved_quantity_positive",
		"skus",
		type_="check",
		schema="catalog",
	)
