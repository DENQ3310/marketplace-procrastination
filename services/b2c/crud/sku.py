from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from database.models import Sku


async def get_sku_by_id(db: AsyncSession, sku_id: uuid.UUID) -> Sku | None:
	"""
	Gets SKU by its ID
	:param db: database session
	:param sku_id: SKU ID
	:return: SKU or None if not found
	"""
	result = await db.execute(select(Sku).where(Sku.id == sku_id))
	return result.scalars().first()
