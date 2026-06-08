from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from crud import category as category_crud
from database.models.catalog.base import Category
from schemas.category import CategoryCreate
from exceptions.category import CategoryNotFoundError


async def create_new_category(
	db: AsyncSession, category_in: CategoryCreate
) -> Category:
	return await category_crud.create_category(db, category_in)


async def get_category_or_404(db: AsyncSession, category_id: UUID) -> Category:
	category = await category_crud.get_category_by_id(db, category_id)
	if not category:
		raise CategoryNotFoundError()
	return category


async def list_categories(
	db: AsyncSession, parent_id: UUID | None = None
) -> list[Category]:
	return await category_crud.get_all_categories(db, parent_id)
