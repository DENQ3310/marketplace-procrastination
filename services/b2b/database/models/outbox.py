import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.core import Base


class OutboxEventStatus(str, enum.Enum):
	PENDING = "PENDING"
	SENT = "SENT"


class OutboxEvent(Base):
	__tablename__ = "outbox_events"
	__table_args__ = {"schema": "catalog"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	idempotency_key: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True)
	event_type: Mapped[str] = mapped_column(String(128))
	routing_key: Mapped[str] = mapped_column(String(255))
	payload: Mapped[dict] = mapped_column(JSONB)
	status: Mapped[OutboxEventStatus] = mapped_column(
		default=OutboxEventStatus.PENDING, server_default="PENDING"
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
	sent_at: Mapped[datetime | None] = mapped_column(
		DateTime(timezone=True), nullable=True
	)
