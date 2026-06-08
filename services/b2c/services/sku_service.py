import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from crud import sku as sku_crud
from database.models import Sku
from exceptions.sku import SkuNotFoundError


async def get_sku_by_id(db: AsyncSession, sku_id: uuid.UUID) -> Sku:
	"""
	Gets a SKU by its ID
	:param db: database session
	:param sku_id: SKU ID
	:return: SKU or None if not found
	"""
	sku = await sku_crud.get_sku_by_id(db, sku_id)
	if not sku:
		raise SkuNotFoundError

	return sku
