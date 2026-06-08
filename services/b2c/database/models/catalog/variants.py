import uuid
from datetime import datetime

from sqlalchemy import (
	String,
	BigInteger,
	DateTime,
	ForeignKey,
	CheckConstraint,
	text,
	func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.core import Base


class Sku(Base):
	__tablename__ = "skus"
	__table_args__ = (
		CheckConstraint("active_quantity >= 0", name="chk_active_quantity_positive"),
		CheckConstraint(
			"reserved_quantity >= 0", name="chk_reserved_quantity_positive"
		),
		{"schema": "catalog"},
	)

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	product_id: Mapped[uuid.UUID] = mapped_column(
		ForeignKey("catalog.products.id", ondelete="CASCADE")
	)
	name: Mapped[str] = mapped_column(String(255))
	price: Mapped[int] = mapped_column(BigInteger)
	discount: Mapped[int] = mapped_column(default=0, server_default="0")
	active_quantity: Mapped[int] = mapped_column(default=0, server_default="0")
	reserved_quantity: Mapped[int] = mapped_column(default=0, server_default="0")
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
	)
	product = relationship("Product", back_populates="skus")
	images = relationship("Image", foreign_keys="Image.sku_id")
	characteristics = relationship(
		"Characteristic", foreign_keys="Characteristic.sku_id"
	)


class Characteristic(Base):
	__tablename__ = "characteristics"
	__table_args__ = (
		CheckConstraint(
			"product_id IS NOT NULL OR sku_id IS NOT NULL",
			name="chk_characteristic_owner",
		),
		{"schema": "catalog"},
	)

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	product_id: Mapped[uuid.UUID | None] = mapped_column(
		ForeignKey("catalog.products.id", ondelete="CASCADE")
	)
	sku_id: Mapped[uuid.UUID | None] = mapped_column(
		ForeignKey("catalog.skus.id", ondelete="CASCADE")
	)
	name: Mapped[str] = mapped_column(String(255))
	value: Mapped[str] = mapped_column(String(255))

	product = relationship(
		"Product", back_populates="characteristics", foreign_keys=[product_id]
	)


class Image(Base):
	__tablename__ = "images"
	__table_args__ = {"schema": "catalog"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	product_id: Mapped[uuid.UUID] = mapped_column(
		ForeignKey("catalog.products.id", ondelete="CASCADE")
	)
	sku_id: Mapped[uuid.UUID | None] = mapped_column(
		ForeignKey("catalog.skus.id", ondelete="CASCADE")
	)
	url: Mapped[str] = mapped_column(String(512))
	ordering: Mapped[int] = mapped_column(default=0, server_default="0")

	product = relationship(
		"Product", back_populates="images", foreign_keys=[product_id]
	)
