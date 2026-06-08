import uuid
from datetime import datetime, date

from sqlalchemy import String, Text, DateTime, Date, ForeignKey, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.core import Base


class Banner(Base):
	__tablename__ = "banners"
	__table_args__ = {"schema": "storefront"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	title: Mapped[str] = mapped_column(String(255))
	image_url: Mapped[str] = mapped_column(String(512))
	link: Mapped[str] = mapped_column(String(512))
	priority: Mapped[int] = mapped_column(default=0, server_default="0")
	is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
	start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)


class Collection(Base):
	__tablename__ = "collections"
	__table_args__ = {"schema": "storefront"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	title: Mapped[str] = mapped_column(String(255))
	description: Mapped[str | None] = mapped_column(Text)
	cover_image_url: Mapped[str | None] = mapped_column(String(512))
	target_url: Mapped[str | None] = mapped_column(String(512))
	priority: Mapped[int] = mapped_column(default=0, server_default="0")
	start_date: Mapped[date | None] = mapped_column(Date)
	is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)


class CollectionProduct(Base):
	__tablename__ = "collection_products"
	__table_args__ = {"schema": "storefront"}

	collection_id: Mapped[uuid.UUID] = mapped_column(
		ForeignKey("storefront.collections.id", ondelete="CASCADE"), primary_key=True
	)
	product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
