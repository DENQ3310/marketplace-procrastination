import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, text, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


from database.core import Base

if TYPE_CHECKING:
	from database.models.cart.item import CartItem
	from database.models.personal.profile import Favorite, Subscription


class User(Base):
	__tablename__ = "users"
	__table_args__ = {"schema": "identity"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	username: Mapped[str] = mapped_column(unique=True, nullable=False)
	email: Mapped[str] = mapped_column(unique=True, nullable=False)
	password_hash: Mapped[str] = mapped_column(nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)

	# Relationships
	cart_items: Mapped[list["CartItem"]] = relationship(
		"CartItem", back_populates="user", foreign_keys="CartItem.user_id"
	)
	favorites: Mapped[list["Favorite"]] = relationship(
		"Favorite", back_populates="user"
	)
	subscriptions: Mapped[list["Subscription"]] = relationship(
		"Subscription", back_populates="user"
	)


class Session(Base):
	__tablename__ = "sessions"
	__table_args__ = {"schema": "identity"}

	session_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
	token: Mapped[str] = mapped_column(unique=True, nullable=False)
	refresh_token: Mapped[str] = mapped_column(unique=True, nullable=False)
	issued_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
	expires_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), nullable=False
	)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Seller(Base):
	__tablename__ = "sellers"
	__table_args__ = {"schema": "identity"}

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
	)
	email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
	password_hash: Mapped[str] = mapped_column(unique=True, nullable=False)
	first_name: Mapped[str] = mapped_column(nullable=False)
	last_name: Mapped[str] = mapped_column(nullable=False)
	middle_name: Mapped[str] = mapped_column()  # Can be empty
	company_name: Mapped[str] = mapped_column(nullable=False)
	phone: Mapped[str] = mapped_column(unique=True)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now()
	)
