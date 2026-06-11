import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.core import Base


class ModerationProcessedEvent(Base):
	__tablename__ = "moderation_processed_events"
	__table_args__ = {"schema": "catalog"}

	idempotency_key: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True
	)
	product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	status: Mapped[str] = mapped_column(String(32), nullable=False)
	processed_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
