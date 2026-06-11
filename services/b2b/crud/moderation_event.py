from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.catalog.base import Product
from database.models.moderation_event import ModerationProcessedEvent


async def lock_idempotency_key(db: AsyncSession, idempotency_key: UUID) -> None:
	unsigned_key = idempotency_key.int & ((1 << 63) - 1)
	await db.execute(select(func.pg_advisory_xact_lock(unsigned_key)))


async def get_processed_event(
	db: AsyncSession, idempotency_key: UUID
) -> ModerationProcessedEvent | None:
	result = await db.execute(
		select(ModerationProcessedEvent).where(
			ModerationProcessedEvent.idempotency_key == idempotency_key
		)
	)
	return result.scalar_one_or_none()


async def lock_product(db: AsyncSession, product_id: UUID) -> Product | None:
	result = await db.execute(
		select(Product).where(Product.id == product_id).with_for_update()
	)
	return result.scalar_one_or_none()


def add_processed_event(
	db: AsyncSession,
	idempotency_key: UUID,
	product_id: UUID,
	status: str,
) -> ModerationProcessedEvent:
	event = ModerationProcessedEvent(
		idempotency_key=idempotency_key,
		product_id=product_id,
		status=status,
	)
	db.add(event)
	return event
