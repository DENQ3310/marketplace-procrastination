import uuid

from sqlalchemy import BigInteger, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import CheckConstraint

from database.core import Base


class OrderItem(Base):
	__tablename__ = "order_items"
	__table_args__ = (
		CheckConstraint("quantity > 0", name="chk_order_item_quantity_positive"),
		CheckConstraint(
			"unit_price >= 0", name="chk_order_item_unit_price_nonnegative"
		),
		{"schema": "orders"},
	)

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	order_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("orders.orders.id", ondelete="CASCADE")
	)
	sku_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
	product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
	product_title: Mapped[str] = mapped_column(String(255))
	sku_name: Mapped[str] = mapped_column(String(255))
	quantity: Mapped[int] = mapped_column(Integer)
	unit_price: Mapped[int] = mapped_column(BigInteger)
	line_total: Mapped[int] = mapped_column(BigInteger)
	image_url: Mapped[str | None] = mapped_column(String(512))
	order = relationship("Order", back_populates="items")
