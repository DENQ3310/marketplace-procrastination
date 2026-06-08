"""update_image_schema

Revision ID: ebe1c33fa4b8
Revises: 83e4a34fab48
Create Date: 2026-05-22 12:12:47.036379

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ebe1c33fa4b8"
down_revision: Union[str, Sequence[str], None] = "83e4a34fab48"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Upgrade schema."""
	op.execute("""
			CREATE TYPE public.imageentitytypeenum
			AS ENUM ('PRODUCT', 'SKU');
	""")

	# op.execute("ALTER TABLE catalog.images DROP CONSTRAINT images_product_id_fky;")
	# op.execute("ALTER TABLE catalog.images DROP CONSTRAINT images_sku_id_fky;")
	op.execute("ALTER TABLE catalog.images DROP COLUMN product_id;")
	op.execute("ALTER TABLE catalog.images DROP COLUMN sku_id;")
	op.execute("ALTER TABLE catalog.images ADD COLUMN entity_id UUID;")
	op.execute(
		"ALTER TABLE catalog.images ADD COLUMN entity_type public.imageentitytypeenum;"
	)


def downgrade() -> None:
	"""Downgrade schema."""
	# Revert changes to images table
	op.execute("ALTER TABLE catalog.images DROP COLUMN entity_type;")
	op.execute("ALTER TABLE catalog.images DROP COLUMN entity_id;")
	op.execute("ALTER TABLE catalog.images ADD COLUMN sku_id UUID;")
	op.execute("ALTER TABLE catalog.images ADD COLUMN product_id UUID NOT NULL;")
	op.execute(
		"ALTER TABLE catalog.images ADD CONSTRAINT images_product_id_fkey "
		"FOREIGN KEY (product_id) REFERENCES catalog.products(id) ON DELETE CASCADE;"
	)
	op.execute(
		"ALTER TABLE catalog.images ADD CONSTRAINT images_sku_id_fkey "
		"FOREIGN KEY (sku_id) REFERENCES catalog.skus(id) ON DELETE CASCADE;"
	)
	op.execute("DROP TYPE public.imageentitytypeenum;")
