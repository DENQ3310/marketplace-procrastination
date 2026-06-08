import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, Text, DateTime, ForeignKey, Index, text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from database.core import Base


class ProductStatusEnum(str, enum.Enum):
	CREATED = "CREATED"
	ON_MODERATION = "ON_MODERATION"
	MODERATED = "MODERATED"
	BLOCKED = "BLOCKED"
	HARD_BLOCKED = "HARD_BLOCKED"


class Product(Base):
	__tablename__ = "products"
	__table_args__ = (
		Index("idx_products_seller_id", "seller_id"),
		{"schema": "catalog"},
	)

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	seller_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
	category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("catalog.categories.id"))
	title: Mapped[str] = mapped_column(String(255))
	slug: Mapped[str] = mapped_column(String(255), unique=True)
	description: Mapped[str | None] = mapped_column(Text)
	status: Mapped[ProductStatusEnum] = mapped_column(
		default=ProductStatusEnum.CREATED, server_default="CREATED"
	)
	deleted: Mapped[bool] = mapped_column(Boolean, default=False)
	blocked_reason_id: Mapped[uuid.UUID | None] = mapped_column(
		UUID, nullable=True, server_default=None
	)
	blocking_reason_title: Mapped[str | None] = mapped_column(
		String(255), nullable=True
	)
	moderator_comment: Mapped[str] = mapped_column(
		String(1000), default="", server_default=""
	)
	field_reports: Mapped[list] = mapped_column(JSONB, server_default="[]")
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
	)


class Category(Base):
	__tablename__ = "categories"
	__table_args__ = {"schema": "catalog"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	parent_id: Mapped[uuid.UUID | None] = mapped_column(
		ForeignKey("catalog.categories.id", ondelete="SET NULL")
	)
	name: Mapped[str] = mapped_column(String(255))
	slug: Mapped[str] = mapped_column(String(255), unique=True)
	description: Mapped[str | None] = mapped_column(Text)
	is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
