"""add-user-schema

Revision ID: ed153fa1e43c
Revises: 3ed06920443b
Create Date: 2026-05-15 10:30:09.361032

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "ed153fa1e43c"
down_revision: Union[str, None] = "3ed06920443b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.execute("CREATE SCHEMA IF NOT EXISTS identity")

	op.create_table(
		"sellers",
		sa.Column(
			"id",
			UUID(as_uuid=True),
			server_default=sa.text("gen_random_uuid()"),
			nullable=False,
		),
		sa.Column("email", sa.String(), nullable=False),
		sa.Column("password_hash", sa.String(), nullable=False),
		sa.Column("first_name", sa.String(), nullable=False),
		sa.Column("last_name", sa.String(), nullable=False),
		sa.Column("middle_name", sa.String(), nullable=True),
		sa.Column("company_name", sa.String(), nullable=False),
		sa.Column("phone", sa.String(), nullable=True),
		sa.PrimaryKeyConstraint("id", name=op.f("sellers_pkey")),
		sa.UniqueConstraint("email", name=op.f("sellers_email_key")),
		sa.UniqueConstraint("password_hash", name=op.f("sellers_password_hash_key")),
		sa.UniqueConstraint("phone", name=op.f("sellers_phone_key")),
		schema="identity",
	)

	op.execute(
		"ALTER TABLE catalog.products "
		"ADD CONSTRAINT fk_products_seller_id "
		"FOREIGN KEY (seller_id) "
		"REFERENCES identity.sellers(id);"
	)

	op.create_table(
		"sessions",
		sa.Column(
			"id",
			UUID(as_uuid=True),
			server_default=sa.text("gen_random_uuid()"),
			nullable=False,
		),
		sa.Column("user_id", UUID(as_uuid=True)),
		sa.Column("access_token", sa.String(), nullable=False),
		sa.Column("refresh_token", sa.String(), nullable=False),
		sa.Column(
			"issued_at", sa.DateTime(timezone=True), server_default=sa.func.now()
		),
		sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
		sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
		sa.PrimaryKeyConstraint("id", name=op.f("sessions_pkey")),
		sa.ForeignKeyConstraint(
			["user_id"],
			["identity.sellers.id"],
			name=op.f("fk_sessions_user_id_sellers"),
		),
		sa.UniqueConstraint("access_token", name=op.f("uq_sessions_access_token")),
		sa.UniqueConstraint("refresh_token", name=op.f("uq_sessions_refresh_token")),
		schema="identity",
	)


def downgrade() -> None:
	op.drop_table("sessions", schema="identity")

	op.execute(
		"ALTER TABLE catalog.products DROP CONSTRAINT IF EXISTS fk_products_seller_id;"
	)

	op.drop_table("sellers", schema="identity")
