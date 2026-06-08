import secrets


from database.models import Seller, Session
from exceptions.session import SessionNotFoundError
from schemas.auth import LoginRequest, RefreshRequest, TokenResponse, SellerCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import crud.seller as seller_crud
import crud.session as session_crud
from exceptions.seller import (
	InvalidPasswordError,
	SellerAlreadyExistsError,
	SellerNotFoundError,
)
from core import security
from core.config import settings

from datetime import datetime, timezone


async def register(data: SellerCreate, db: AsyncSession) -> TokenResponse:
	seller = Seller(
		email=data.email,
		first_name=data.first_name,
		last_name=data.last_name,
		middle_name=data.middle_name,
		company_name=data.company_name,
		phone=data.phone,
		password_hash=security.get_password_hash(data.password),
	)

	try:
		seller = await seller_crud.add_seller(seller, db)
	except IntegrityError as e:  # Some data that should be unique isn't
		raise SellerAlreadyExistsError(e) from e

	return await create_session(seller.id, db)


async def create_session(user_id: str, db: AsyncSession) -> TokenResponse:
	access_token: str = security.create_access_token(user_id)
	refresh_token: str = secrets.token_urlsafe(32)

	session = Session(
		user_id=user_id,
		access_token=access_token,
		refresh_token=refresh_token,
		expires_at=datetime.now(timezone.utc),
	)

	session = await session_crud.add_session(session, db)

	return TokenResponse(
		user_id=session.user_id,
		access_token=access_token,
		refresh_token=refresh_token,
		token_type="bearer",  # noqa
		expires_in=settings.SESSION_EXPIRE_SECONDS,
	)


def validate_password(password: str) -> bool:
	return len(password) >= 8


async def login(data: LoginRequest, db: AsyncSession) -> TokenResponse:
	seller: Seller | None = await seller_crud.get_seller_by_email(data.email, db)

	if not seller:
		raise SellerNotFoundError()

	if not security.verify_password(data.password, seller.password_hash):
		raise InvalidPasswordError()

	session = await create_session(seller.id, db)

	return session


async def logout(refresh_token: str, db: AsyncSession) -> None:
	if await session_crud.deactivate_session(refresh_token, db):
		return
	raise SessionNotFoundError


async def refresh(refresh_token: RefreshRequest, db: AsyncSession) -> TokenResponse:
	session: Session | None = await session_crud.get_session_by_refresh_token(
		refresh_token, db
	)

	if not session:
		raise SessionNotFoundError("session not found 1")

	new_token = security.create_access_token(session.user_id)

	session = await session_crud.update_session_access_token(session, new_token, db)

	if not session:
		raise SessionNotFoundError("session not found 2")

	return TokenResponse(
		user_id=session.user_id,
		access_token=session.access_token,
		refresh_token=session.refresh_token,
		token_type="Bearer",  # noqa
		expires_in=settings.SESSION_EXPIRE_SECONDS,
	)
