import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.core import Base


class FulfilledOrder(Base):
	__tablename__ = "fulfilled_orders"
	__table_args__ = {"schema": "catalog"}

	order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
	items: Mapped[list[dict]] = mapped_column(JSONB)
	result: Mapped[list[dict]] = mapped_column(JSONB)
	fulfilled_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
