from sqlalchemy.ext.asyncio import AsyncSession

import crud.category as category_crud
import crud.collection as collection_crud
import crud.review as review_crud
from schemas.collection import Collection
from services.schemas_builder import build_catalog_product_cards


async def get_catalog_collections(db: AsyncSession) -> list[Collection]:
	total_count = await collection_crud.count_active_collections(db)
	if total_count == 0:
		return []

	collections_db = await collection_crud.get_active_collections(
		db, limit=total_count, offset=0
	)
	if not collections_db:
		return []

	collection_ids = [collection.id for collection in collections_db]
	product_ids_by_collection = await collection_crud.get_product_ids_by_collection_ids(
		db, collection_ids
	)
	all_product_ids = list(
		{
			product_id
			for product_ids in product_ids_by_collection.values()
			for product_id in product_ids
		}
	)

	products = await collection_crud.get_available_catalog_products_by_ids(
		db, all_product_ids
	)
	categories_map = await category_crud.get_all_categories_map(db)
	review_stats_by_product = await review_crud.get_reviews_stats_by_product_ids(
		db, [product.id for product in products]
	)
	product_cards = build_catalog_product_cards(
		products, categories_map, review_stats_by_product
	)
	cards_by_product_id = {card.id: card for card in product_cards}

	result: list[Collection] = []
	for collection in collections_db:
		product_ids = product_ids_by_collection.get(collection.id, [])
		products = [
			cards_by_product_id[product_id]
			for product_id in product_ids
			if product_id in cards_by_product_id
		]
		result.append(
			Collection(
				id=collection.id,
				name=collection.title,
				description=collection.description or "",
				products=products,
			)
		)
	return result
