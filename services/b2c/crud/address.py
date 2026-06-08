import uuid

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.personal.address import Address


async def get_address_by_id_for_user(
	db: AsyncSession, address_id: uuid.UUID, user_id: uuid.UUID
) -> Address | None:
	result: Result = await db.execute(
		select(Address).where(Address.id == address_id, Address.user_id == user_id)
	)
	return result.scalar_one_or_none()
