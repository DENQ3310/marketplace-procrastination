import uuid

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from crud import images as images_crud
from crud import product as product_crud
from database.models.catalog.base import Product, ProductStatusEnum
from database.models.catalog.variants import Characteristic, Image, Sku
from schemas.public_catalog import PublicSort


def _apply_visibility(query: Select) -> Select:
	in_stock = select(Sku.product_id).where(Sku.active_quantity > 0)
	return query.where(
		Product.status == ProductStatusEnum.MODERATED,
		Product.deleted.is_(False),
		Product.id.in_(in_stock),
	)


async def list_visible_products(
	db: AsyncSession,
	limit: int,
	offset: int,
	category_id: uuid.UUID | None = None,
	search: str | None = None,
	seller_id: uuid.UUID | None = None,
	min_price: int | None = None,
	max_price: int | None = None,
	sort: PublicSort = "created_desc",
) -> tuple[list[Product], int]:
	query = select(Product)
	count_query = select(func.count(Product.id))

	query = _apply_visibility(query)
	count_query = _apply_visibility(count_query)

	if category_id is not None:
		query = query.where(Product.category_id == category_id)
		count_query = count_query.where(Product.category_id == category_id)

	if seller_id is not None:
		query = query.where(Product.seller_id == seller_id)
		count_query = count_query.where(Product.seller_id == seller_id)

	if search:
		search_val = search.strip()
		if len(search_val) >= 3:
			escaped = (
				search_val.replace("/", "//").replace("%", "/%").replace("_", "/_")
			)
			term = f"%{escaped}%"
			search_condition = or_(
				Product.title.ilike(term, escape="/"),
				Product.description.ilike(term, escape="/"),
			)
			query = query.where(search_condition)
			count_query = count_query.where(search_condition)

	min_price_sq = (
		select(
			Sku.product_id.label("product_id"),
			func.min(Sku.price).label("min_price"),
		)
		.where(Sku.active_quantity > 0)
		.group_by(Sku.product_id)
		.subquery()
	)
	if (
		min_price is not None
		or max_price is not None
		or sort
		in (
			"price_asc",
			"price_desc",
		)
	):
		query = query.join(min_price_sq, Product.id == min_price_sq.c.product_id)
		count_query = count_query.join(
			min_price_sq, Product.id == min_price_sq.c.product_id
		)
		if min_price is not None:
			query = query.where(min_price_sq.c.min_price >= min_price)
			count_query = count_query.where(min_price_sq.c.min_price >= min_price)
		if max_price is not None:
			query = query.where(min_price_sq.c.min_price <= max_price)
			count_query = count_query.where(min_price_sq.c.min_price <= max_price)

	match sort:
		case "price_asc":
			query = query.order_by(min_price_sq.c.min_price.asc())
		case "price_desc":
			query = query.order_by(min_price_sq.c.min_price.desc())
		case "popular" | "created_desc":
			query = query.order_by(Product.created_at.desc())

	query = query.offset(offset).limit(limit)

	total = (await db.execute(count_query)).scalar() or 0
	products = list((await db.execute(query)).scalars().all())
	return products, int(total)


async def get_visible_products_by_ids(
	db: AsyncSession, product_ids: list[uuid.UUID]
) -> list[Product]:
	if not product_ids:
		return []

	query = _apply_visibility(select(Product)).where(Product.id.in_(product_ids))
	result = await db.execute(query)
	by_id = {product.id: product for product in result.scalars().all()}
	return [by_id[pid] for pid in product_ids if pid in by_id]


async def get_visible_product_by_id(
	db: AsyncSession, product_id: uuid.UUID
) -> Product | None:
	query = _apply_visibility(select(Product)).where(Product.id == product_id)
	return (await db.execute(query)).scalar_one_or_none()


async def get_in_stock_skus_for_products(
	db: AsyncSession, product_ids: list[uuid.UUID]
) -> dict[uuid.UUID, list[Sku]]:
	if not product_ids:
		return {}

	result = await db.execute(
		select(Sku)
		.options(joinedload(Sku.characteristics))
		.where(
			Sku.product_id.in_(product_ids),
			Sku.active_quantity > 0,
		)
	)
	grouped: dict[uuid.UUID, list[Sku]] = {}
	for sku in result.unique().scalars().all():
		grouped.setdefault(sku.product_id, []).append(sku)
	return grouped


async def load_public_catalog_list_page(
	db: AsyncSession,
	limit: int,
	offset: int,
	category_id: uuid.UUID | None = None,
	search: str | None = None,
	seller_id: uuid.UUID | None = None,
	min_price: int | None = None,
	max_price: int | None = None,
	sort: PublicSort = "created_desc",
) -> tuple[
	list[Product], int, dict[uuid.UUID, list[Image]], dict[uuid.UUID, list[Sku]]
]:
	products, total = await list_visible_products(
		db,
		limit,
		offset,
		category_id,
		search,
		seller_id,
		min_price,
		max_price,
		sort,
	)
	if not products:
		return [], total, {}, {}

	product_ids = [product.id for product in products]
	images_by_product = await images_crud.get_product_images_for_products(
		db, product_ids
	)
	skus_by_product = await get_in_stock_skus_for_products(db, product_ids)
	return products, total, images_by_product, skus_by_product


async def load_public_products_details(
	db: AsyncSession, products: list[Product]
) -> list[
	tuple[
		Product,
		list[Image],
		list[Characteristic],
		list[Sku],
		dict[uuid.UUID, list[Image]],
	]
]:
	if not products:
		return []

	product_ids = [product.id for product in products]
	images_by_product = await images_crud.get_product_images_for_products(
		db, product_ids
	)
	characteristics_by_product = (
		await product_crud.get_product_characteristics_for_products(db, product_ids)
	)
	skus_by_product = await get_in_stock_skus_for_products(db, product_ids)
	sku_ids = [sku.id for skus in skus_by_product.values() for sku in skus]
	sku_images_by_sku = await images_crud.get_sku_images_for_sku_ids(db, sku_ids)

	return [
		(
			product,
			images_by_product.get(product.id, []),
			characteristics_by_product.get(product.id, []),
			skus_by_product.get(product.id, []),
			sku_images_by_sku,
		)
		for product in products
	]


async def load_public_product_details(
	db: AsyncSession, product_id: uuid.UUID
) -> (
	tuple[
		Product,
		list[Image],
		list[Characteristic],
		list[Sku],
		dict[uuid.UUID, list[Image]],
	]
	| None
):
	product = await get_visible_product_by_id(db, product_id)
	if product is None:
		return None
	rows = await load_public_products_details(db, [product])
	return rows[0] if rows else None


async def load_public_products_details_bundles(
	db: AsyncSession, product_ids: list[uuid.UUID]
) -> list[
	tuple[
		Product,
		list[Image],
		list[Characteristic],
		list[Sku],
		dict[uuid.UUID, list[Image]],
	]
]:
	products = await get_visible_products_by_ids(db, product_ids)
	return await load_public_products_details(db, products)
