from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Result, select
import uuid
from database.models import Category, FilterValues
from exceptions.category import CategoryNotFoundError


async def get_all_categories_map(
	db: AsyncSession,
) -> dict[uuid.UUID, Category]:
	result = await db.execute(select(Category))
	return {category.id: category for category in result.scalars().all()}


async def get_category_by_id(
	db: AsyncSession, category_id: uuid.UUID
) -> Category | None:
	result: Result[Tuple[Category]] = await db.execute(
		select(Category).where(Category.id == category_id)
	)
	return result.scalars().first()


async def get_categories_by_parent_id(
	db: AsyncSession, parent_id: uuid.UUID | None
) -> list[Category]:
	result: Result[Tuple[Category]] = await db.execute(
		select(Category).where(Category.parent_id == parent_id)
	)
	return result.scalars().all()


async def get_category_filters(db: AsyncSession, category_id: uuid.UUID) -> list:
	from database.models.catalog.base import CategoryFilters

	exists = await db.execute(select(Category.id).where(Category.id == category_id))
	if not exists.scalars().first():
		raise CategoryNotFoundError(f"Category with id {category_id} not found")

	filters = await db.execute(
		select(CategoryFilters).where(CategoryFilters.category_id == category_id)
	)
	return filters.scalars().all()


async def get_filter_values(db: AsyncSession, filter_id: uuid.UUID) -> list[str]:
	result = await db.execute(
		select(FilterValues.value).where(FilterValues.filter_id == filter_id)
	)
	return result.scalars().all()
