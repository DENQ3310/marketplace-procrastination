import uuid

from sqlalchemy.ext.asyncio import AsyncSession

import crud.favorite as favorite_crud
from exceptions.product import ProductNotFoundError
from schemas.catalog import PaginatedCatalogProducts
from services.schemas_builder import build_catalog_product_cards


async def get_favorites_list(
	db: AsyncSession, user_id: uuid.UUID, limit: int, offset: int
) -> PaginatedCatalogProducts:
	data = await favorite_crud.get_available_favorites_data(db, user_id, limit, offset)
	items = build_catalog_product_cards(
		data.products, data.categories_map, data.review_stats_by_product
	)
	return PaginatedCatalogProducts(
		items=items,
		total_count=data.total_count,
		limit=limit,
		offset=offset,
	)


async def add_to_favorites(
	db: AsyncSession, user_id: uuid.UUID, product_id: uuid.UUID
) -> None:
	if await favorite_crud.get_favorite(db, user_id, product_id):
		return

	if not await favorite_crud.check_product_exists_and_available(db, product_id):
		raise ProductNotFoundError("Товар не найден")

	await favorite_crud.add_favorite(db, user_id, product_id)


async def remove_from_favorites(
	db: AsyncSession, user_id: uuid.UUID, product_id: uuid.UUID
) -> None:
	await favorite_crud.remove_favorite(db, user_id, product_id)
