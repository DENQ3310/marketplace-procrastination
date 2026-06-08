import uuid
from dataclasses import dataclass
from typing import List, Tuple, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import crud.category as category_crud
import crud.review as review_crud
from crud.review import ProductReviewStats
from database.models import Favorite, Product, Sku
from database.models.catalog.base import Category, ProductStatusEnum


@dataclass(frozen=True, slots=True)
class AvailableFavoritesData:
	products: list[Product]
	total_count: int
	categories_map: dict[uuid.UUID, Category]
	review_stats_by_product: dict[uuid.UUID, ProductReviewStats]


async def get_user_favorites(
	db: AsyncSession, user_id: uuid.UUID, limit: int, offset: int
) -> Tuple[List[Favorite], int]:
	count_result = await db.execute(
		select(func.count(Favorite.product_id)).where(Favorite.user_id == user_id)
	)
	total_count = count_result.scalar() or 0

	result = await db.execute(
		select(Favorite)
		.where(Favorite.user_id == user_id)
		.options(
			selectinload(Favorite.product).selectinload(Product.category),
			selectinload(Favorite.product).selectinload(Product.images),
			selectinload(Favorite.product).selectinload(Product.skus),
		)
		.order_by(Favorite.added_at.desc())
		.limit(limit)
		.offset(offset)
	)
	favorites = list(result.scalars().all())
	return favorites, total_count


async def add_favorite(
	db: AsyncSession, user_id: uuid.UUID, product_id: uuid.UUID
) -> Favorite:
	result = await db.execute(
		select(Favorite)
		.where(Favorite.user_id == user_id, Favorite.product_id == product_id)
		.options(
			selectinload(Favorite.product).selectinload(Product.category),
			selectinload(Favorite.product).selectinload(Product.images),
			selectinload(Favorite.product).selectinload(Product.skus),
		)
	)
	existing = result.scalar_one_or_none()
	if existing:
		return existing

	favorite = Favorite(user_id=user_id, product_id=product_id)
	db.add(favorite)
	await db.flush()
	await db.commit()

	result = await db.execute(
		select(Favorite)
		.where(Favorite.user_id == user_id, Favorite.product_id == product_id)
		.options(
			selectinload(Favorite.product).selectinload(Product.category),
			selectinload(Favorite.product).selectinload(Product.images),
			selectinload(Favorite.product).selectinload(Product.skus),
		)
	)
	return result.scalar_one()


async def remove_favorite(
	db: AsyncSession, user_id: uuid.UUID, product_id: uuid.UUID
) -> bool:
	result = await db.execute(
		select(Favorite).where(
			Favorite.user_id == user_id, Favorite.product_id == product_id
		)
	)
	favorite = result.scalar_one_or_none()
	if not favorite:
		return False

	await db.delete(favorite)
	await db.commit()
	return True


async def check_product_exists_and_available(
	db: AsyncSession, product_id: uuid.UUID
) -> bool:
	result = await db.execute(
		select(Product).where(
			Product.id == product_id,
			Product.status == ProductStatusEnum.MODERATED,
			Product.id.in_(select(Sku.product_id).where(Sku.active_quantity > 0)),
		)
	)
	return result.scalar_one_or_none() is not None


async def get_available_favorites(
	db: AsyncSession, user_id: uuid.UUID, limit: int, offset: int
) -> Tuple[List[Favorite], int]:
	available_product_ids = select(Product.id).where(
		Product.status == ProductStatusEnum.MODERATED,
		Product.id.in_(select(Sku.product_id).where(Sku.active_quantity > 0)),
	)

	count_result = await db.execute(
		select(func.count(Favorite.product_id)).where(
			Favorite.user_id == user_id, Favorite.product_id.in_(available_product_ids)
		)
	)
	total_count = count_result.scalar() or 0

	result = await db.execute(
		select(Favorite)
		.where(
			Favorite.user_id == user_id, Favorite.product_id.in_(available_product_ids)
		)
		.options(
			selectinload(Favorite.product).selectinload(Product.category),
			selectinload(Favorite.product).selectinload(Product.images),
			selectinload(Favorite.product).selectinload(Product.skus),
			selectinload(Favorite.product).selectinload(Product.seller),
		)
		.order_by(Favorite.added_at.desc())
		.limit(limit)
		.offset(offset)
	)
	favorites = list(result.scalars().all())
	return favorites, total_count


async def get_available_favorites_data(
	db: AsyncSession, user_id: uuid.UUID, limit: int, offset: int
) -> AvailableFavoritesData:
	favorites, total_count = await get_available_favorites(db, user_id, limit, offset)
	products = [favorite.product for favorite in favorites]
	product_ids = [product.id for product in products]
	return AvailableFavoritesData(
		products=products,
		total_count=total_count,
		categories_map=await category_crud.get_all_categories_map(db),
		review_stats_by_product=await review_crud.get_reviews_stats_by_product_ids(
			db, product_ids
		),
	)


async def get_favorite(
	db: AsyncSession, user_id: uuid.UUID, product_id: uuid.UUID
) -> Optional[Favorite]:
	result = await db.execute(
		select(Favorite).where(
			Favorite.user_id == user_id, Favorite.product_id == product_id
		)
	)
	return result.scalar_one_or_none()
