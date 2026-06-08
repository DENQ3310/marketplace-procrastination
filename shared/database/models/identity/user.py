import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from shared.database.core import Base


class RoleEnum(str, enum.Enum):
	SELLER = "SELLER"
	BUYER = "BUYER"
	ADMIN = "ADMIN"


class User(Base):
	__tablename__ = "users"
	__table_args__ = {"schema": "identity"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	role: Mapped[RoleEnum] = mapped_column(
		default=RoleEnum.BUYER, server_default="BUYER"
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
