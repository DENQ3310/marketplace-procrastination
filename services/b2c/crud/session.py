from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result

from typing import Tuple
import datetime


from database.models import Session
from core.config import settings

import uuid


async def create_session(
	user_id: uuid.UUID, access_token: str, refresh_token: str, db: AsyncSession
) -> Session:
	session = Session(
		user_id=user_id,
		token=access_token,
		refresh_token=refresh_token,
		expires_at=datetime.datetime.now(datetime.timezone.utc)
		+ datetime.timedelta(seconds=settings.SESSION_EXPIRE_SECONDS),
	)

	db.add(session)

	await db.commit()

	await db.refresh(session)

	return session


async def get_session_by_token(token: str, db: AsyncSession) -> Session | None:
	result: Result[Tuple[Session]] = await db.execute(
		select(Session).where(Session.token == token)
	)
	return result.scalars().one_or_none()


async def check_active_session(token: str, db: AsyncSession) -> bool:
	result = await db.execute(select(Session).where(Session.token == token))
	session = result.scalar_one_or_none()
	if session:
		return session.is_active
	return False


async def deactivate_session(token: str, db: AsyncSession) -> bool:
	result = await db.execute(select(Session).where(Session.token == token))
	session = result.scalar_one_or_none()

	if session:
		session.is_active = False
		await db.flush()
		await db.commit()
		return True
	return False


async def get_session_by_refresh_token(token: str, db: AsyncSession) -> Session | None:
	result = await db.execute(select(Session).where(Session.refresh_token == token))

	session = result.scalar_one_or_none()

	return session


async def update_session_token(
	session: Session, new_token: str, db: AsyncSession
) -> Session:
	db.add(session)
	session.token = new_token
	session.issued_at = datetime.datetime.now(datetime.timezone.utc)
	session.expires_at = session.issued_at + datetime.timedelta(
		seconds=settings.SESSION_EXPIRE_SECONDS
	)
	await db.commit()
	await db.refresh(session)

	return session
