from uuid import UUID

from crud import outbox as outbox_crud
from database.models.catalog.base import Product, ProductStatusEnum
from database.models.catalog.variants import (
	Characteristic,
	Image,
	ImageEntityTypeEnum,
	Sku,
)
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def submit_for_moderation(
	db: AsyncSession,
	product: Product,
	event: str = "CREATED",
) -> None:
	product.status = ProductStatusEnum.ON_MODERATION
	db.add(product)
	await outbox_crud.enqueue_moderation_product_event(
		db,
		product_id=product.id,
		seller_id=product.seller_id,
		event=event,
	)


async def add_product(
	product: Product,
	db: AsyncSession,
	images: list[dict],
	characteristics: list[dict],
) -> tuple[Product, list[Image], list[Characteristic]]:
	db.add(product)
	await db.flush()

	product_images = [
		Image(
			entity_type=ImageEntityTypeEnum.PRODUCT,
			entity_id=product.id,
			url=image["url"],
			ordering=image["ordering"],
		)
		for image in images
	]
	product_characteristics = [
		Characteristic(
			product_id=product.id,
			name=characteristic["name"],
			value=characteristic["value"],
		)
		for characteristic in characteristics
	]
	db.add_all([*product_images, *product_characteristics])
	await db.commit()
	await db.refresh(product)
	for image in product_images:
		await db.refresh(image)
	for characteristic in product_characteristics:
		await db.refresh(characteristic)
	return product, product_images, product_characteristics


async def get_seller_products(
	db: AsyncSession,
	seller_id: UUID,
	status: ProductStatusEnum | None = None,
	search: str | None = None,
) -> list[tuple[Product, int, int]]:
	sku_aggregates = (
		select(
			Sku.product_id.label("product_id"),
			func.count(Sku.id).label("skus_count"),
			func.sum(Sku.active_quantity).label("total_active_quantity"),
		)
		.group_by(Sku.product_id)
		.subquery()
	)
	query = (
		select(
			Product,
			func.coalesce(sku_aggregates.c.skus_count, 0),
			func.coalesce(sku_aggregates.c.total_active_quantity, 0),
		)
		.outerjoin(sku_aggregates, Product.id == sku_aggregates.c.product_id)
		.where(Product.seller_id == seller_id)
		.order_by(Product.created_at.desc())
	)
	if status is not None:
		query = query.where(Product.status == status)
	if search:
		escaped = search.strip().replace("/", "//").replace("%", "/%").replace("_", "/_")
		if escaped:
			query = query.where(Product.title.ilike(f"%{escaped}%", escape="/"))

	result = await db.execute(query)
	return [(product, int(count), int(total)) for product, count, total in result.all()]


async def get_product_by_id(
	db: AsyncSession, product_id: UUID, seller_id: UUID
) -> Product | None:
	result = await db.execute(
		select(Product).where(Product.id == product_id, Product.seller_id == seller_id)
	)
	return result.scalar_one_or_none()


async def get_product_by_id_only(
	db: AsyncSession,
	product_id: UUID,
	*,
	for_update: bool = False,
) -> Product | None:
	query = select(Product).where(Product.id == product_id)
	if for_update:
		query = query.with_for_update()
	result = await db.execute(query)
	return result.scalar_one_or_none()


async def get_product_characteristics(
	db: AsyncSession, product_id: UUID
) -> list[Characteristic]:
	result = await db.execute(
		select(Characteristic).where(
			Characteristic.product_id == product_id,
			Characteristic.sku_id.is_(None),
		)
	)
	return list(result.scalars().all())


async def get_product_characteristics_for_products(
	db: AsyncSession, product_ids: list[UUID]
) -> dict[UUID, list[Characteristic]]:
	if not product_ids:
		return {}
	result = await db.execute(
		select(Characteristic).where(
			Characteristic.product_id.in_(product_ids),
			Characteristic.sku_id.is_(None),
		)
	)
	grouped: dict[UUID, list[Characteristic]] = {}
	for characteristic in result.scalars().all():
		if characteristic.product_id is not None:
			grouped.setdefault(characteristic.product_id, []).append(characteristic)
	return grouped


async def update_product(
	db: AsyncSession,
	db_obj: Product,
	update_data: dict,
	should_remoderate: bool = False,
) -> Product:
	characteristics = update_data.pop("characteristics", None)
	for field, value in update_data.items():
		setattr(db_obj, field, value)

	db.add(db_obj)
	if characteristics is not None:
		await db.execute(
			delete(Characteristic).where(
				Characteristic.product_id == db_obj.id,
				Characteristic.sku_id.is_(None),
			)
		)
		db.add_all(
			[
				Characteristic(
					product_id=db_obj.id,
					name=characteristic["name"],
					value=characteristic["value"],
				)
				for characteristic in characteristics
			]
		)
	if should_remoderate:
		await submit_for_moderation(db, db_obj, event="EDITED")

	await db.commit()
	await db.refresh(db_obj)
	return db_obj


async def soft_delete_product(
	db: AsyncSession,
	db_obj: Product,
	sku_ids: list[UUID],
) -> Product:
	db_obj.deleted = True
	db.add(db_obj)
	await outbox_crud.enqueue_product_deleted_events(
		db,
		product_id=db_obj.id,
		seller_id=db_obj.seller_id,
		sku_ids=sku_ids,
	)
	await db.commit()
	await db.refresh(db_obj)
	return db_obj


async def hard_delete_product(db: AsyncSession, db_obj: Product) -> None:
	await db.delete(db_obj)
	await db.commit()
