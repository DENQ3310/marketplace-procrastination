import enum
import uuid
from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Index, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.core import Base
from database.models.identity.user import Seller


class ProductStatusEnum(str, enum.Enum):
	CREATED = "CREATED"
	ON_MODERATION = "ON_MODERATION"
	MODERATED = "MODERATED"
	BLOCKED = "BLOCKED"


class FilterTypeEnum(str, enum.Enum):
	LIST = "LIST"
	RANGE = "RANGE"
	SWITCH = "SWITCH"


class Product(Base):
	__tablename__ = "products"
	__table_args__ = (
		Index("idx_products_seller_id", "seller_id"),
		{"schema": "catalog"},
	)

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	seller_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("identity.sellers.id")
	)
	category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("catalog.categories.id"))
	title: Mapped[str] = mapped_column(String(255))
	slug: Mapped[str] = mapped_column(String(255), unique=True)
	description: Mapped[str | None] = mapped_column(Text)
	status: Mapped[ProductStatusEnum] = mapped_column(
		default=ProductStatusEnum.CREATED, server_default="CREATED"
	)
	deleted: Mapped[bool] = mapped_column(default=False, server_default="false")
	rating: Mapped[float] = mapped_column(default=0.0, server_default="0.0")
	popularity: Mapped[int] = mapped_column(default=0, server_default="0")
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
	)

	seller: Mapped["Seller"] = relationship(
		"Seller", lazy="selectin", cascade="save-update"
	)
	category: Mapped["Category"] = relationship("Category", lazy="selectin")
	images = relationship("Image", back_populates="product")
	characteristics = relationship("Characteristic", back_populates="product")
	skus = relationship("Sku", back_populates="product")
	reviews = relationship("Review", back_populates="product")


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
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
	)
	seo: Mapped[str] = mapped_column(Text, nullable=True)
	image_url: Mapped[str] = mapped_column(String(255), nullable=True)


class CategoryFilters(Base):
	__tablename__ = "category_filters"
	__table_args__ = {"schema": "catalog"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	category_id: Mapped[uuid.UUID] = mapped_column(
		ForeignKey("catalog.categories.id", ondelete="CASCADE")
	)
	name: Mapped[str] = mapped_column(String(255))
	slug: Mapped[str] = mapped_column(String(255), unique=True)
	type: Mapped[FilterTypeEnum] = mapped_column(String(50))
	value: Mapped[str] = mapped_column(
		Text
	)  # Exists beacause of stupid specs. Will be stored in separate table
	min: Mapped[float | None] = mapped_column()
	max: Mapped[float | None] = mapped_column()


class FilterValues(Base):
	__tablename__ = "filter_values"
	__table_args__ = {"schema": "catalog"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	filter_id: Mapped[uuid.UUID] = mapped_column(
		ForeignKey("catalog.category_filters.id", ondelete="CASCADE")
	)
	value: Mapped[str] = mapped_column(String(255))


class ProductFilterValue(Base):
	__tablename__ = "product_filter_values"
	__table_args__ = (
		Index("idx_product_filter_value", "product_id", "filter_value_id"),
		{"schema": "catalog"},
	)

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	product_id: Mapped[uuid.UUID] = mapped_column(
		ForeignKey("catalog.products.id", ondelete="CASCADE")
	)
	filter_value_id: Mapped[uuid.UUID] = mapped_column(
		ForeignKey("catalog.filter_values.id", ondelete="CASCADE")
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)


class Review(Base):
	__tablename__ = "reviews"
	__table_args__ = {"schema": "catalog"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	product_id: Mapped[uuid.UUID] = mapped_column(
		ForeignKey("catalog.products.id", ondelete="CASCADE")
	)
	user_id: Mapped[uuid.UUID] = mapped_column(
		ForeignKey("identity.users.id", ondelete="CASCADE")
	)
	rating: Mapped[int] = mapped_column(Integer, nullable=False)
	comment: Mapped[str] = mapped_column(Text, nullable=False)

	product: Mapped["Product"] = relationship("Product", back_populates="reviews")
