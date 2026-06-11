"""add fulfilled orders

Revision ID: d0b10d202606
Revises: c9b09d202606
Create Date: 2026-06-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "d0b10d202606"
down_revision: Union[str, Sequence[str], None] = "c9b09d202606"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.create_table(
		"fulfilled_orders",
		sa.Column("order_id", sa.UUID(), nullable=False),
		sa.Column(
			"items",
			postgresql.JSONB(astext_type=sa.Text()),
			nullable=False,
		),
		sa.Column(
			"result",
			postgresql.JSONB(astext_type=sa.Text()),
			nullable=False,
		),
		sa.Column(
			"fulfilled_at",
			sa.DateTime(timezone=True),
			server_default=sa.text("now()"),
			nullable=False,
		),
		sa.PrimaryKeyConstraint("order_id"),
		schema="catalog",
	)


def downgrade() -> None:
	op.drop_table("fulfilled_orders", schema="catalog")
