import uuid
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Image, Sku
from database.models.catalog.variants import ImageEntityTypeEnum


async def add_image(image: Image, db: AsyncSession) -> Image:
	db.add(image)
	await db.commit()
	await db.refresh(image)
	return image


async def attach_sku_image(
	db: AsyncSession, sku_id: UUID, url: str, ordering: int = 0
) -> Image:
	image = Image(
		entity_type=ImageEntityTypeEnum.SKU,
		entity_id=sku_id,
		url=url,
		ordering=ordering,
	)
	db.add(image)
	await db.flush()
	return image


async def get_product_images_for_products(
	db: AsyncSession, product_ids: list[uuid.UUID]
) -> dict[uuid.UUID, list[Image]]:
	if not product_ids:
		return {}
	result = await db.execute(
		select(Image)
		.where(
			and_(
				Image.entity_type == ImageEntityTypeEnum.PRODUCT,
				Image.entity_id.in_(product_ids),
			)
		)
		.order_by(Image.ordering)
	)
	grouped: dict[uuid.UUID, list[Image]] = {}
	for image in result.scalars().all():
		grouped.setdefault(image.entity_id, []).append(image)
	return grouped


async def get_product_images_by_id(
	product_id: uuid.UUID, db: AsyncSession
) -> list[Image]:
	result = await db.execute(
		select(Image).where(
			and_(
				Image.entity_type == ImageEntityTypeEnum.PRODUCT,
				Image.entity_id == product_id,
			)
		)
	)
	return list(result.scalars().all())


async def get_sku_images_for_sku_ids(
	db: AsyncSession, sku_ids: list[uuid.UUID]
) -> dict[uuid.UUID, list[Image]]:
	if not sku_ids:
		return {}
	result = await db.execute(
		select(Image)
		.where(
			and_(
				Image.entity_type == ImageEntityTypeEnum.SKU,
				Image.entity_id.in_(sku_ids),
			)
		)
		.order_by(Image.ordering)
	)
	grouped: dict[uuid.UUID, list[Image]] = {}
	for image in result.scalars().all():
		grouped.setdefault(image.entity_id, []).append(image)
	return grouped


async def get_sku_images_by_id(sku_id: uuid.UUID, db: AsyncSession) -> list[Image]:
	result = await db.execute(
		select(Image).where(
			and_(
				Image.entity_type == ImageEntityTypeEnum.SKU,
				Image.entity_id == sku_id,
			)
		)
	)
	return list(result.scalars().all())


async def product_has_sku_image(db: AsyncSession, product_id: UUID) -> bool:
	result = await db.execute(
		select(func.count())
		.select_from(Image)
		.join(
			Sku,
			and_(
				Image.entity_id == Sku.id,
				Image.entity_type == ImageEntityTypeEnum.SKU,
			),
		)
		.where(Sku.product_id == product_id)
	)
	return int(result.scalar_one()) > 0
