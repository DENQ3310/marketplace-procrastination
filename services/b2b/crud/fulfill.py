from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.catalog.variants import Sku
from database.models.fulfilled_order import FulfilledOrder


async def lock_order_id(db: AsyncSession, order_id: UUID) -> None:
	unsigned_key = (order_id.int & ((1 << 63) - 1)) ^ 3
	await db.execute(select(func.pg_advisory_xact_lock(unsigned_key)))


async def get_fulfilled_order(
	db: AsyncSession, order_id: UUID
) -> FulfilledOrder | None:
	result = await db.execute(
		select(FulfilledOrder).where(FulfilledOrder.order_id == order_id)
	)
	return result.scalar_one_or_none()


async def lock_skus(db: AsyncSession, sku_ids: list[UUID]) -> list[Sku]:
	result = await db.execute(
		select(Sku).where(Sku.id.in_(sku_ids)).order_by(Sku.id).with_for_update()
	)
	return list(result.scalars().all())


def add_fulfilled_order(
	db: AsyncSession,
	order_id: UUID,
	items: list[dict],
	result: list[dict],
) -> FulfilledOrder:
	order = FulfilledOrder(order_id=order_id, items=items, result=result)
	db.add(order)
	return order
