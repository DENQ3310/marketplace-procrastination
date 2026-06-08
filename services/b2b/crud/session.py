from database.models import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone


async def add_session(session: Session, db: AsyncSession) -> Session:
	db.add(session)
	await db.commit()
	await db.refresh(session)
	return session


async def deactivate_session(token: str, db: AsyncSession) -> bool:
	result = await db.execute(select(Session).where(Session.refresh_token == token))
	session = result.scalar_one_or_none()

	if session:
		session.is_active = False
		await db.flush()
		await db.commit()
		return True
	return False


async def get_session_by_refresh_token(
	refresh_token: str, db: AsyncSession
) -> Session | None:
	result = await db.execute(
		select(Session).where(Session.refresh_token == refresh_token)
	)
	return result.scalar_one_or_none()


async def update_session_access_token(
	session: Session, new_token: str, db: AsyncSession
) -> Session:
	session.acccess_token = new_token
	session.issued_at = datetime.now(timezone.utc)

	await db.flush()

	await db.refresh(session)

	return session


async def get_session_by_access_token(
	access_token: str, db: AsyncSession
) -> Session | None:
	result = await db.execute(
		select(Session).where(Session.access_token == access_token)
	)
	return result.scalar_one_or_none()


async def check_active_session(token: str, db: AsyncSession) -> bool:
	result = await db.execute(select(Session).where(Session.access_token == token))
	session = result.scalar_one_or_none()
	if session:
		return session.is_active
	return False
