from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from database.models.catalog.base import Category
from schemas.category import CategoryCreate


async def create_category(db: AsyncSession, category_in: CategoryCreate) -> Category:
	db_obj = Category(**category_in.model_dump())
	db.add(db_obj)
	await db.commit()
	await db.refresh(db_obj)
	return db_obj


async def get_category_by_id(db: AsyncSession, category_id: UUID) -> Category | None:
	result = await db.execute(select(Category).where(Category.id == category_id))
	return result.scalars().first()


async def get_all_categories(
	db: AsyncSession, parent_id: UUID | None = None
) -> list[Category]:
	query = select(Category).where(Category.parent_id == parent_id)
	result = await db.execute(query)
	return result.scalars().all()
