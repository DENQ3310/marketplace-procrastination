import uuid
from datetime import datetime
from sqlalchemy import DateTime, Index, UniqueConstraint, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from shared.database.core import Base


class Favorite(Base):
	__tablename__ = "favorites"
	__table_args__ = (
		Index("idx_favorites_user", "user_id"),
		{"schema": "personal"},
	)

	user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
	product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
	added_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)


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

	user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
	product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))

	notify_in_stock: Mapped[bool] = mapped_column(default=False, server_default="false")
	notify_price_down: Mapped[bool] = mapped_column(
		default=False, server_default="false"
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
