"""store inventory operation result

Revision ID: b8b08d202606
Revises: a8b08d202606
Create Date: 2026-06-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "b8b08d202606"
down_revision: Union[str, Sequence[str], None] = "a8b08d202606"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column(
		"inventory_operations",
		sa.Column(
			"result",
			postgresql.JSONB(astext_type=sa.Text()),
			nullable=True,
		),
		schema="catalog",
	)


def downgrade() -> None:
	op.drop_column("inventory_operations", "result", schema="catalog")
