from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from crud import public_product as public_product_crud
from database.models.catalog.base import Product
from database.models.catalog.variants import Characteristic, Image, Sku
from exceptions.product import ProductNotFoundError
from schemas.product import CharacteristicsResponse, ProductImageResponse
from schemas.public_catalog import (
	ProductPublicPaginatedResponse,
	ProductPublicResponse,
	ProductPublicShortResponse,
	PublicSort,
	SkuPublicResponse,
)

PublicProductDetails = tuple[
	Product,
	list[Image],
	list[Characteristic],
	list[Sku],
	dict[UUID, list[Image]],
]


def build_product_public_response(row: PublicProductDetails) -> ProductPublicResponse:
	product, images, characteristics, skus, sku_images_by_sku = row
	return ProductPublicResponse(
		id=product.id,
		seller_id=product.seller_id,
		category_id=product.category_id,
		title=product.title,
		slug=product.slug,
		description=product.description or "",
		status=product.status,
		images=[
			ProductImageResponse(id=img.id, url=img.url, ordering=img.ordering)
			for img in images
		],
		characteristics=[
			CharacteristicsResponse(id=c.id, name=c.name, value=c.value)
			for c in characteristics
		],
		skus=[
			SkuPublicResponse(
				id=sku.id,
				product_id=sku.product_id,
				name=sku.name,
				price=sku.price,
				discount=sku.discount,
				stock_quantity=sku.stock_quantity,
				active_quantity=sku.active_quantity,
				article=sku.article or None,
				images=[
					ProductImageResponse(id=img.id, url=img.url, ordering=img.ordering)
					for img in sku_images_by_sku.get(sku.id, [])
				],
				characteristics=[
					CharacteristicsResponse(id=c.id, name=c.name, value=c.value)
					for c in sku.characteristics
				],
			)
			for sku in skus
		],
		created_at=product.created_at,
		updated_at=product.updated_at,
	)


def build_product_public_short(
	product: Product,
	min_price: int,
	cover_image: str | None,
) -> ProductPublicShortResponse:
	return ProductPublicShortResponse(
		id=product.id,
		title=product.title,
		slug=product.slug,
		status=product.status,
		category_id=product.category_id,
		min_price=min_price,
		cover_image=cover_image,
		created_at=product.created_at,
	)


async def list_public_catalog(
	db: AsyncSession,
	limit: int,
	offset: int,
	category_id: UUID | None,
	search: str | None,
	seller_id: UUID | None,
	min_price: int | None,
	max_price: int | None,
	sort: PublicSort,
	product_ids: list[UUID] | None = None,
) -> ProductPublicPaginatedResponse:
	(
		products,
		total,
		images_by_product,
		skus_by_product,
	) = await public_product_crud.load_public_catalog_list_page(
		db,
		limit,
		offset,
		category_id,
		search,
		seller_id,
		min_price,
		max_price,
		sort,
		product_ids,
	)

	items = []
	for product in products:
		product_images = images_by_product.get(product.id, [])
		product_skus = skus_by_product.get(product.id, [])
		cover_image = None
		if product_images:
			cover_image = sorted(product_images, key=lambda img: img.ordering)[0].url
		min_sku_price = min((sku.price for sku in product_skus), default=0)
		items.append(build_product_public_short(product, min_sku_price, cover_image))

	return ProductPublicPaginatedResponse(
		items=items,
		total_count=total,
		limit=limit,
		offset=offset,
	)


async def batch_public_products(
	db: AsyncSession, product_ids: list[UUID]
) -> list[ProductPublicResponse]:
	rows = await public_product_crud.load_public_products_details_bundles(
		db, product_ids
	)
	return [build_product_public_response(row) for row in rows]


async def get_public_product_for_b2c(
	db: AsyncSession, product_id: UUID
) -> ProductPublicResponse:
	row = await public_product_crud.load_public_product_details(db, product_id)
	if row is None:
		raise ProductNotFoundError("Product not found")
	return build_product_public_response(row)
