import uuid

from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.personal.payment_method import PaymentMethod


async def get_payment_method_by_id_for_user(
	db: AsyncSession, method_id: uuid.UUID, user_id: uuid.UUID
) -> PaymentMethod | None:
	result: Result = await db.execute(
		select(PaymentMethod).where(
			PaymentMethod.id == method_id, PaymentMethod.user_id == user_id
		)
	)
	return result.scalar_one_or_none()
