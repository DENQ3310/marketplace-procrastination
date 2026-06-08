import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.core import Base


class PaymentMethodTypeEnum(str, enum.Enum):
	CARD = "CARD"
	SBP = "SBP"
	WALLET = "WALLET"


class PaymentMethod(Base):
	__tablename__ = "payment_methods"
	__table_args__ = {"schema": "personal"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	user_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), ForeignKey("identity.users.id", ondelete="CASCADE")
	)
	type: Mapped[PaymentMethodTypeEnum] = mapped_column(
		default=PaymentMethodTypeEnum.CARD, server_default="CARD"
	)
	card_last4: Mapped[str | None] = mapped_column(String(4))
	card_brand: Mapped[str | None] = mapped_column(String(20))
	is_default: Mapped[bool] = mapped_column(
		Boolean, default=False, server_default="false"
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
	user = relationship("User")
