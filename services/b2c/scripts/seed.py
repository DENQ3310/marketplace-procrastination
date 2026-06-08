# Script for filling db with test data.
# Script for filling db with test data.

import sys
from typing import AsyncGenerator
import uuid
import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from core.db import get_db  # noqa: E402

from database.models.catalog.base import Category, Product  # noqa: E402


db_session: AsyncSession = get_db()


async def clear_db(db_session: AsyncSession) -> None:
	await db_session.execute(delete(Product))
	await db_session.execute(delete(Category))
	await db_session.commit()


async def generate_categories(db_session: AsyncSession) -> None:
	"""Generates test categories."""

	# Root category
	root_category: Category = Category(
		name="Root Category",
		slug="root-category",
		description="This is the root category.",
	)

	# Commit root category to get its ID
	db_session.add(root_category)
	await db_session.commit()
	await db_session.refresh(root_category)

	root_category_id: uuid.UUID = root_category.id

	subcategories: list[Category] = [
		Category(
			name=f"Subcategory {i}",
			slug=f"subcategory-{i}",
			description=f"This is subcategory {i}.",
			parent_id=root_category_id,
		)
		for i in range(1, 4)
	]

	# Commit subcategories to the database
	for category in subcategories:
		db_session.add(category)
	await db_session.commit()


async def main() -> None:
	db_gen: AsyncGenerator[AsyncSession, None] = get_db()
	db: AsyncSession = await db_gen.__anext__()
	await clear_db(db)
	await generate_categories(db)


if __name__ == "__main__":
	asyncio.run(main())
