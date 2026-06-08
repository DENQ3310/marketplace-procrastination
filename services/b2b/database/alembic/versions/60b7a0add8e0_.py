"""

Revision ID: 60b7a0add8e0
Revises: ed153fa1e43c
Create Date: 2026-05-19 08:05:29.039847

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "60b7a0add8e0"
down_revision: Union[str, Sequence[str], None] = "ed153fa1e43c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Upgrade schema."""
	op.add_column(
		"sellers",
		sa.Column(
			"created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
		),
		schema="identity",
	)
	op.add_column(
		"sellers",
		sa.Column(
			"updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
		),
		schema="identity",
	)


def downgrade() -> None:
	"""Downgrade schema."""
	op.drop_column("sellers", "updated_at", schema="identity")
	op.drop_column("sellers", "created_at", schema="identity")
	# ### end Alembic commands ###
