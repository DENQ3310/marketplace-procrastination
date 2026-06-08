import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.core import Base


class Address(Base):
	__tablename__ = "addresses"
	__table_args__ = {"schema": "personal"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	user_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("identity.users.id", ondelete="CASCADE")
	)

	country: Mapped[str] = mapped_column(String(100))
	region: Mapped[str | None] = mapped_column(String(200))
	city: Mapped[str] = mapped_column(String(200))
	street: Mapped[str] = mapped_column(String(200))
	building: Mapped[str] = mapped_column(String(50))
	apartment: Mapped[str | None] = mapped_column(String(50))
	postal_code: Mapped[str | None] = mapped_column(String(20))

	recipient_name: Mapped[str | None] = mapped_column(String(200))
	recipient_phone: Mapped[str | None] = mapped_column(String(20))
	is_default: Mapped[bool] = mapped_column(
		Boolean, default=False, server_default="false"
	)
	comment: Mapped[str | None] = mapped_column(String(500))

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)

	user = relationship("User")
