from dataclasses import dataclass
import secrets

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import crud.session as session_crud
from core.security import create_access_token
from database.models.catalog.base import Category, ProductStatusEnum
from database.models.catalog.variants import (
	Sku,
	Product,
	Characteristic,
	Image,
	ImageEntityTypeEnum,
)
from database.models import Session
from database.models.identity.identity import Seller
from tests.factories.catalog import CategoryFactory, ProductFactory, SkuFactory

import uuid

from datetime import datetime, timezone, timedelta

from tests.factories.seller import SellerFactory


@dataclass(frozen=True, slots=True)
class CategoryWithProductsData:
	categories: list[Category]
	products: list[Product]
	skus: list[Sku]


@dataclass(frozen=True, slots=True)
class CreateProductData:
	seller: Seller
	category: Category


@pytest.fixture
async def create_product_data(db_session: AsyncSession) -> CreateProductData:
	seller: Seller = SellerFactory.build()

	db_session.add(seller)
	await db_session.commit()
	await db_session.refresh(seller)

	category = CategoryFactory.build()

	db_session.add(category)
	await db_session.commit()
	await db_session.refresh(category)

	return CreateProductData(seller=seller, category=category)


async def auth_headers(user_id: uuid.UUID, db: AsyncSession) -> dict:
	token = create_access_token(user_id)
	if not await session_crud.check_active_session(token, db):
		session = Session(
			user_id=user_id,
			access_token=token,
			refresh_token=secrets.token_hex(32),
			expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
		)
		await session_crud.add_session(session, db)

	return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
async def category_with_products(
	db_session: AsyncSession,
) -> CategoryWithProductsData:
	seller: Seller = SellerFactory.build()
	db_session.add(seller)
	await db_session.commit()
	await db_session.refresh(seller)

	categories = []
	products = []
	skus = []
	for _ in range(3):
		category = CategoryFactory.build()
		db_session.add(category)
		await db_session.commit()
		categories.append(category)
		for _ in range(3):
			product = ProductFactory.build(
				category_id=category.id,
				seller_id=seller.id,
				status=ProductStatusEnum.MODERATED,
			)
			db_session.add(product)
			await db_session.commit()
			products.append(product)
			for _ in range(3):
				sku = SkuFactory.build(product_id=product.id)
				db_session.add(sku)
				await db_session.commit()
				skus.append(sku)

	db_session.add_all([*categories, *products, *skus])
	await db_session.commit()
	return CategoryWithProductsData(categories, products, skus)


@pytest.fixture()
async def product_no_skus(
	db_session: AsyncSession,
) -> CategoryWithProductsData:
	seller: Seller = SellerFactory.build()
	db_session.add(seller)
	await db_session.commit()
	await db_session.refresh(seller)

	categories = []
	products = []
	skus = []
	for _ in range(3):
		category = CategoryFactory.build()
		db_session.add(category)
		await db_session.commit()
		categories.append(category)
		for _ in range(3):
			product = ProductFactory.build(
				category_id=category.id,
				seller_id=seller.id,
				status=ProductStatusEnum.CREATED,
			)
			db_session.add(product)
			await db_session.commit()
			products.append(product)
		db_session.add_all([*categories, *products])
	await db_session.commit()
	return CategoryWithProductsData(categories, products, skus)


@dataclass(frozen=True, slots=True)
class EditProductData:
	owner: Seller
	other_seller: Seller
	category: Category
	moderated_product: Product
	moderated_sku: Sku
	reserved_sku: Sku
	blocked_product: Product
	blocked_sku: Sku
	hard_blocked_product: Product
	hard_blocked_sku: Sku
	other_seller_product: Product
	other_seller_sku: Sku


@dataclass(frozen=True, slots=True)
class DeleteProductData:
	owner: Seller
	other_seller: Seller
	product: Product
	skus: list[Sku]
	other_seller_product: Product


@dataclass(frozen=True, slots=True)
class CreateInvoiceData:
	owner: Seller
	moderated_sku: Sku
	non_moderated_sku: Sku
	other_seller_sku: Sku


@pytest.fixture()
async def create_invoice_data(db_session: AsyncSession) -> CreateInvoiceData:
	owner: Seller = SellerFactory.build()
	other_seller: Seller = SellerFactory.build()
	category = CategoryFactory.build()
	db_session.add_all([owner, other_seller, category])
	await db_session.flush()

	moderated_product = ProductFactory.build(
		category_id=category.id,
		seller_id=owner.id,
		status=ProductStatusEnum.MODERATED,
	)
	non_moderated_product = ProductFactory.build(
		category_id=category.id,
		seller_id=owner.id,
		status=ProductStatusEnum.ON_MODERATION,
	)
	other_seller_product = ProductFactory.build(
		category_id=category.id,
		seller_id=other_seller.id,
		status=ProductStatusEnum.MODERATED,
	)
	db_session.add_all(
		[moderated_product, non_moderated_product, other_seller_product]
	)
	await db_session.flush()

	moderated_sku = SkuFactory.build(product_id=moderated_product.id)
	non_moderated_sku = SkuFactory.build(product_id=non_moderated_product.id)
	other_seller_sku = SkuFactory.build(product_id=other_seller_product.id)
	db_session.add_all([moderated_sku, non_moderated_sku, other_seller_sku])
	await db_session.commit()

	return CreateInvoiceData(
		owner=owner,
		moderated_sku=moderated_sku,
		non_moderated_sku=non_moderated_sku,
		other_seller_sku=other_seller_sku,
	)


@pytest.fixture()
async def delete_product_data(db_session: AsyncSession) -> DeleteProductData:
	owner: Seller = SellerFactory.build()
	other_seller: Seller = SellerFactory.build()
	category = CategoryFactory.build()
	db_session.add_all([owner, other_seller, category])
	await db_session.flush()

	product = ProductFactory.build(
		category_id=category.id,
		seller_id=owner.id,
		status=ProductStatusEnum.MODERATED,
	)
	other_seller_product = ProductFactory.build(
		category_id=category.id,
		seller_id=other_seller.id,
		status=ProductStatusEnum.MODERATED,
	)
	db_session.add_all([product, other_seller_product])
	await db_session.flush()

	skus = [
		SkuFactory.build(product_id=product.id),
		SkuFactory.build(product_id=product.id),
	]
	db_session.add_all(skus)
	await db_session.commit()

	return DeleteProductData(
		owner=owner,
		other_seller=other_seller,
		product=product,
		skus=skus,
		other_seller_product=other_seller_product,
	)


@pytest.fixture()
async def hard_blocked_product(
	db_session: AsyncSession,
) -> CategoryWithProductsData:
	seller: Seller = SellerFactory.build()
	db_session.add(seller)
	await db_session.commit()
	await db_session.refresh(seller)

	category = CategoryFactory.build()
	product = ProductFactory.build(
		category_id=category.id,
		seller_id=seller.id,
		status=ProductStatusEnum.HARD_BLOCKED,
	)
	sku = SkuFactory.build(product_id=product.id)
	db_session.add_all([category, product, sku])
	await db_session.commit()
	return CategoryWithProductsData([category], [product], [sku])


@pytest.fixture()
async def product_on_moderation_with_one_sku(
	db_session: AsyncSession,
) -> CategoryWithProductsData:
	seller: Seller = SellerFactory.build()
	db_session.add(seller)
	await db_session.commit()
	await db_session.refresh(seller)

	category = CategoryFactory.build()
	product = ProductFactory.build(
		category_id=category.id,
		seller_id=seller.id,
		status=ProductStatusEnum.ON_MODERATION,
	)
	sku = SkuFactory.build(product_id=product.id)
	db_session.add_all([category, product, sku])
	await db_session.commit()
	return CategoryWithProductsData([category], [product], [sku])


@pytest.fixture()
async def blocked_product(
	db_session: AsyncSession,
) -> CategoryWithProductsData:
	seller: Seller = SellerFactory.build()
	db_session.add(seller)
	await db_session.commit()
	await db_session.refresh(seller)

	category = CategoryFactory.build()
	product = ProductFactory.build(
		category_id=category.id,
		seller_id=seller.id,
		status=ProductStatusEnum.BLOCKED,
	)
	sku = SkuFactory.build(product_id=product.id)
	db_session.add_all([category, product, sku])
	await db_session.commit()
	return CategoryWithProductsData([category], [product], [sku])


@pytest.fixture()
async def edit_product_data(
	db_session: AsyncSession,
) -> EditProductData:
	owner: Seller = SellerFactory.build()
	other_seller: Seller = SellerFactory.build()
	db_session.add_all([owner, other_seller])
	await db_session.commit()
	await db_session.refresh(owner)
	await db_session.refresh(other_seller)

	category = CategoryFactory.build()
	db_session.add(category)
	await db_session.commit()
	await db_session.refresh(category)

	moderated_product = ProductFactory.build(
		category_id=category.id,
		seller_id=owner.id,
		status=ProductStatusEnum.MODERATED,
	)
	blocked_product = ProductFactory.build(
		category_id=category.id,
		seller_id=owner.id,
		status=ProductStatusEnum.BLOCKED,
	)
	hard_blocked_product = ProductFactory.build(
		category_id=category.id,
		seller_id=owner.id,
		status=ProductStatusEnum.HARD_BLOCKED,
	)
	other_seller_product = ProductFactory.build(
		category_id=category.id,
		seller_id=other_seller.id,
		status=ProductStatusEnum.MODERATED,
	)
	db_session.add_all(
		[
			moderated_product,
			blocked_product,
			hard_blocked_product,
			other_seller_product,
		]
	)
	await db_session.commit()

	moderated_sku = SkuFactory.build(product_id=moderated_product.id)
	reserved_sku = SkuFactory.build(
		product_id=moderated_product.id,
		reserved_quantity=5,
		active_quantity=10,
	)
	blocked_sku = SkuFactory.build(product_id=blocked_product.id)
	hard_blocked_sku = SkuFactory.build(product_id=hard_blocked_product.id)
	other_seller_sku = SkuFactory.build(product_id=other_seller_product.id)
	db_session.add_all(
		[
			moderated_sku,
			reserved_sku,
			blocked_sku,
			hard_blocked_sku,
			other_seller_sku,
		]
	)
	await db_session.commit()

	return EditProductData(
		owner=owner,
		other_seller=other_seller,
		category=category,
		moderated_product=moderated_product,
		moderated_sku=moderated_sku,
		reserved_sku=reserved_sku,
		blocked_product=blocked_product,
		blocked_sku=blocked_sku,
		hard_blocked_product=hard_blocked_product,
		hard_blocked_sku=hard_blocked_sku,
		other_seller_product=other_seller_product,
		other_seller_sku=other_seller_sku,
	)


@dataclass(frozen=True, slots=True)
class ViewProductData:
	owner: Seller
	other_seller: Seller
	category: Category
	products_by_status: dict[ProductStatusEnum, Product]
	moderated_product: Product
	moderated_sku: Sku
	blocked_product: Product
	blocked_sku: Sku
	other_seller_product: Product
	blocking_reason_id: uuid.UUID


@pytest.fixture()
async def view_product_data(db_session: AsyncSession) -> ViewProductData:
	owner: Seller = SellerFactory.build()
	other_seller: Seller = SellerFactory.build()
	db_session.add_all([owner, other_seller])
	await db_session.commit()
	await db_session.refresh(owner)
	await db_session.refresh(other_seller)

	category = CategoryFactory.build()
	db_session.add(category)
	await db_session.commit()
	await db_session.refresh(category)

	moderated_product = ProductFactory.build(
		category_id=category.id,
		seller_id=owner.id,
		status=ProductStatusEnum.MODERATED,
	)
	blocking_reason_id = uuid.uuid4()
	blocked_product = ProductFactory.build(
		category_id=category.id,
		seller_id=owner.id,
		status=ProductStatusEnum.BLOCKED,
		blocked_reason_id=blocking_reason_id,
		blocking_reason_title="Описание не соответствует товару",
		moderator_comment="Несоответствие описания и фотографий",
	)
	other_seller_product = ProductFactory.build(
		category_id=category.id,
		seller_id=other_seller.id,
		status=ProductStatusEnum.MODERATED,
	)
	created_product = ProductFactory.build(
		category_id=category.id,
		seller_id=owner.id,
		status=ProductStatusEnum.CREATED,
	)
	on_moderation_product = ProductFactory.build(
		category_id=category.id,
		seller_id=owner.id,
		status=ProductStatusEnum.ON_MODERATION,
	)
	hard_blocked_product = ProductFactory.build(
		category_id=category.id,
		seller_id=owner.id,
		status=ProductStatusEnum.HARD_BLOCKED,
		blocked_reason_id=uuid.uuid4(),
		blocking_reason_title="Repeated policy violations",
		moderator_comment="Contact support for details",
	)
	db_session.add_all(
		[
			moderated_product,
			blocked_product,
			created_product,
			on_moderation_product,
			hard_blocked_product,
			other_seller_product,
		]
	)
	await db_session.commit()

	moderated_sku = SkuFactory.build(
		product_id=moderated_product.id,
		cost_price=9500000,
		reserved_quantity=2,
		active_quantity=10,
	)
	blocked_sku = SkuFactory.build(
		product_id=blocked_product.id,
		cost_price=450000,
	)
	other_seller_sku = SkuFactory.build(product_id=other_seller_product.id)
	db_session.add_all([moderated_sku, blocked_sku, other_seller_sku])
	await db_session.flush()

	blocked_product.field_reports = [
		{
			"field_name": "description",
			"sku_id": None,
			"comment": "В описании указан неверный материал",
		},
		{
			"field_name": "sku_image",
			"sku_id": str(blocked_sku.id),
			"comment": "Фото SKU не соответствует указанному цвету",
		},
	]

	product_char = Characteristic(
		product_id=moderated_product.id,
		name="Бренд",
		value="Apple",
	)
	product_image = Image(
		entity_type=ImageEntityTypeEnum.PRODUCT,
		entity_id=moderated_product.id,
		url="/s3/iphone15-front.jpg",
		ordering=0,
	)
	sku_image = Image(
		entity_type=ImageEntityTypeEnum.SKU,
		entity_id=moderated_sku.id,
		url="/s3/iphone15-black-256.jpg",
		ordering=0,
	)
	db_session.add_all([product_char, product_image, sku_image])
	await db_session.commit()

	return ViewProductData(
		owner=owner,
		other_seller=other_seller,
		category=category,
		products_by_status={
			ProductStatusEnum.CREATED: created_product,
			ProductStatusEnum.ON_MODERATION: on_moderation_product,
			ProductStatusEnum.MODERATED: moderated_product,
			ProductStatusEnum.BLOCKED: blocked_product,
			ProductStatusEnum.HARD_BLOCKED: hard_blocked_product,
		},
		moderated_product=moderated_product,
		moderated_sku=moderated_sku,
		blocked_product=blocked_product,
		blocked_sku=blocked_sku,
		other_seller_product=other_seller_product,
		blocking_reason_id=blocking_reason_id,
	)


PUBLIC_CATALOG_SERVICE_KEY_HEADERS = {"X-Service-Key": "test-b2c-service-key"}


@dataclass(frozen=True, slots=True)
class PublicCatalogData:
	visible_product: Product
	visible_sku: Sku
	hard_blocked_product: Product
	out_of_stock_product: Product
	on_moderation_product: Product


@pytest.fixture()
async def public_catalog_data(db_session: AsyncSession) -> PublicCatalogData:
	category = CategoryFactory.build()
	db_session.add(category)
	await db_session.flush()

	visible_product = ProductFactory.build(
		category_id=category.id,
		status=ProductStatusEnum.MODERATED,
		deleted=False,
		slug=f"visible-{uuid.uuid4().hex[:8]}",
	)
	hard_blocked_product = ProductFactory.build(
		category_id=category.id,
		status=ProductStatusEnum.HARD_BLOCKED,
		deleted=False,
		slug=f"hard-blocked-{uuid.uuid4().hex[:8]}",
	)
	out_of_stock_product = ProductFactory.build(
		category_id=category.id,
		status=ProductStatusEnum.MODERATED,
		deleted=False,
		slug=f"oos-{uuid.uuid4().hex[:8]}",
	)
	on_moderation_product = ProductFactory.build(
		category_id=category.id,
		status=ProductStatusEnum.ON_MODERATION,
		deleted=False,
		slug=f"moderating-{uuid.uuid4().hex[:8]}",
	)
	db_session.add_all(
		[
			visible_product,
			hard_blocked_product,
			out_of_stock_product,
			on_moderation_product,
		]
	)
	await db_session.flush()

	visible_sku = SkuFactory.build(
		product_id=visible_product.id,
		active_quantity=5,
		cost_price=12345,
		reserved_quantity=2,
	)
	hard_blocked_sku = SkuFactory.build(
		product_id=hard_blocked_product.id,
		active_quantity=3,
	)
	oos_sku = SkuFactory.build(product_id=out_of_stock_product.id, active_quantity=0)
	moderating_sku = SkuFactory.build(
		product_id=on_moderation_product.id, active_quantity=10
	)
	db_session.add_all([visible_sku, hard_blocked_sku, oos_sku, moderating_sku])
	await db_session.commit()

	return PublicCatalogData(
		visible_product=visible_product,
		visible_sku=visible_sku,
		hard_blocked_product=hard_blocked_product,
		out_of_stock_product=out_of_stock_product,
		on_moderation_product=on_moderation_product,
	)
