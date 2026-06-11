"""add moderation processed events

Revision ID: c9b09d202606
Revises: b8b08d202606
Create Date: 2026-06-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c9b09d202606"
down_revision: Union[str, Sequence[str], None] = "b8b08d202606"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.create_table(
		"moderation_processed_events",
		sa.Column("idempotency_key", sa.UUID(), nullable=False),
		sa.Column("product_id", sa.UUID(), nullable=False),
		sa.Column("status", sa.String(length=32), nullable=False),
		sa.Column(
			"processed_at",
			sa.DateTime(timezone=True),
			server_default=sa.text("now()"),
			nullable=False,
		),
		sa.PrimaryKeyConstraint("idempotency_key"),
		schema="catalog",
	)


def downgrade() -> None:
	op.drop_table("moderation_processed_events", schema="catalog")
