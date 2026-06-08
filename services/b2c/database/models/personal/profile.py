import uuid
from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.models.catalog.base import Product

from database.core import Base

if TYPE_CHECKING:
	from database.models.identity.user import User


class Favorite(Base):
	__tablename__ = "favorites"
	__table_args__ = (
		Index("idx_favorites_user", "user_id"),
		{"schema": "personal"},
	)

	user_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("identity.users.id"), primary_key=True
	)
	product_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("catalog.products.id"), primary_key=True
	)
	added_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)

	# Relationships
	user: Mapped["User"] = relationship("User", back_populates="favorites")
	product: Mapped["Product"] = relationship("Product", foreign_keys=[product_id])


class Subscription(Base):
	__tablename__ = "subscriptions"
	__table_args__ = (
		UniqueConstraint(
			"user_id", "product_id", name="uniq_subscription_user_product"
		),
		{"schema": "personal"},
	)

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)

	user_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("identity.users.id", ondelete="CASCADE")
	)
	product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))

	notify_in_stock: Mapped[bool] = mapped_column(default=False, server_default="false")
	notify_price_down: Mapped[bool] = mapped_column(
		default=False, server_default="false"
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)

	# Relationships
	user: Mapped["User"] = relationship("User", back_populates="subscriptions")
