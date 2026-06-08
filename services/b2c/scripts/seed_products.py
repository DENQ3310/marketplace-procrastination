# Script for filling db with test products in all categories.

import sys
import uuid
import asyncio
import random
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from core.db import get_db  # noqa: E402
from database.models.catalog.base import Category, Product  # noqa: E402
from database.models.catalog.variants import Sku, Image  # noqa: E402


# Sample product data
PRODUCT_NAMES = [
	"Смартфон",
	"Ноутбук",
	"Планшет",
	"Наушники",
	"Клавиатура",
	"Мышь",
	"Монитор",
	"Веб-камера",
	"Микрофон",
	"Колонки",
	"Роутер",
	"Кабель USB",
	"Зарядное устройство",
	"Чехол",
	"Защитное стекло",
	"Флешка",
	"Внешний диск",
	"SSD накопитель",
	"Оперативная память",
	"Видеокарта",
	"Процессор",
	"Материнская плата",
	"Блок питания",
	"Корпус ПК",
	"Кулер",
	"Термопаста",
	"Коврик для мыши",
	"Игровое кресло",
	"Стол компьютерный",
	"Лампа настольная",
]

ADJECTIVES = [
	"Профессиональный",
	"Игровой",
	"Беспроводной",
	"Компактный",
	"Мощный",
	"Стильный",
	"Эргономичный",
	"Премиум",
	"Бюджетный",
	"Универсальный",
	"Портативный",
	"Надежный",
	"Современный",
	"Классический",
	"Инновационный",
]


async def get_all_categories(db: AsyncSession) -> list[Category]:
	"""Get all categories from database."""
	result = await db.execute(select(Category))
	return list(result.scalars().all())


async def create_products_for_category(
	db: AsyncSession, category: Category, count: int = 5
) -> None:
	"""Create test products for a specific category."""

	seller_id = uuid.uuid4()  # Mock seller ID

	for i in range(count):
		# Generate product name
		adjective = random.choice(ADJECTIVES)  # noqa: S311
		base_name = random.choice(PRODUCT_NAMES)  # noqa: S311
		product_name = f"{adjective} {base_name} {i + 1}"
		slug = f"{category.slug}-{base_name.lower().replace(' ', '-')}-{i + 1}-{uuid.uuid4().hex[:8]}"

		# Create product
		product = Product(
			seller_id=seller_id,
			category_id=category.id,
			title=product_name,
			slug=slug,
			description=f"Описание товара: {product_name}. Высокое качество и надежность.",
			status="MODERATED",
		)

		db.add(product)
		await db.flush()  # Get product ID

		# Create 1-3 SKUs for each product
		sku_count = random.randint(1, 3)  # noqa: S311
		for j in range(sku_count):
			base_price = random.randint(1000, 50000)  # noqa: S311
			sku_name = f"{product_name}"

			if sku_count > 1:
				colors = ["Черный", "Белый", "Серый", "Синий", "Красный"]
				sku_name += f" - {colors[j % len(colors)]}"

			sku = Sku(
				product_id=product.id,
				name=sku_name,
				price=base_price,
				active_quantity=random.randint(0, 100),  # noqa: S311
			)

			db.add(sku)

		# Add placeholder image
		image = Image(
			product_id=product.id,
			url=f"https://via.placeholder.com/400x400?text={product_name.replace(' ', '+')}",
			ordering=0,
		)
		db.add(image)

	await db.commit()
	print(f"✓ Created {count} products for category: {category.name}")


async def main() -> None:
	"""Main function to populate database with products."""
	db_gen: AsyncGenerator[AsyncSession, None] = get_db()
	db: AsyncSession = await db_gen.__anext__()

	print("Fetching categories...")
	categories = await get_all_categories(db)

	if not categories:
		print("❌ No categories found! Please run category seeding first.")
		return

	print(f"Found {len(categories)} categories")
	print("Creating products for each category...")

	for category in categories:
		# Create 3-8 products per category
		product_count = random.randint(3, 8)  # noqa: S311
		await create_products_for_category(db, category, product_count)

	print(f"\n✅ Successfully created products for {len(categories)} categories!")


if __name__ == "__main__":
	asyncio.run(main())
