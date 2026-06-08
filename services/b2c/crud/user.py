from typing import Tuple

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


async def get_user_by_username(username: str, db: AsyncSession) -> User | None:
	result: Result[Tuple[User]] = await db.execute(
		select(User).where(User.username == username)
	)
	return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
	result: Result[Tuple[User]] = await db.execute(
		select(User).where(User.email == email)
	)
	return result.scalar_one_or_none()


async def get_user_by_id(id: str, db: AsyncSession) -> User | None:
	result: Result[Tuple[User]] = await db.execute(select(User).where(User.id == id))
	return result.scalar_one_or_none()


async def create_user(user: User, db: AsyncSession) -> User:
	db.add(user)
	await db.commit()
	await db.refresh(user)
	return user
