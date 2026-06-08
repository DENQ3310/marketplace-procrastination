from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import crud.session as session_crud
from core.security import create_access_token
from database.models import Category, Product, ProductStatusEnum, Sku
from database.models.cart.item import CartItem
from database.models.identity.user import User
from database.models.personal.profile import Favorite, Subscription
from database.models.storefront.main import (
	Banner,
	Collection,
	CollectionProduct,
)
from tests.factories.catalog import (
	CartItemFactory,
	CategoryFactory,
	ImageFactory,
	ProductFactory,
	ReviewFactory,
	SkuFactory,
)
from tests.factories.user import UserFactory
from tests.factories.cart import (
	BannerFactory,
	CollectionFactory,
	CollectionProductFactory,
	FavoriteFactory,
	SubscriptionFactory,
)


async def auth_headers(user_id: uuid.UUID, db: AsyncSession) -> dict[str, str]:
	token = create_access_token(user_id)
	if not await session_crud.check_active_session(token, db):
		await session_crud.create_session(user_id, token, str(uuid.uuid4()), db)
	return {"Authorization": f"Bearer {token}"}


@dataclass(frozen=True, slots=True)
class FavoritesData:
	user: User
	categories: list[Category]
	products: list[Product]
	skus: list[Sku]
	favorites: list[Favorite | None]
	subscriptions: list[Subscription | None]


@pytest.fixture()
async def empty_favorites_data(db_session: AsyncSession) -> FavoritesData:
	user = UserFactory.build()
	category = CategoryFactory.build()
	product = ProductFactory.build(category_id=category.id)
	sku = SkuFactory.build(product_id=product.id)
	subscription = SubscriptionFactory.build(user_id=user.id, product_id=product.id)
	db_session.add_all([user, category, product, sku, subscription])
	await db_session.commit()
	return FavoritesData(
		user=user,
		categories=[category],
		products=[product],
		skus=[sku],
		favorites=[None],
		subscriptions=[subscription],
	)


@pytest.fixture()
async def favorites_data(db_session: AsyncSession) -> FavoritesData:
	user = UserFactory.build()
	category = CategoryFactory.build()
	product = ProductFactory.build(category_id=category.id)
	sku = SkuFactory.build(product_id=product.id)
	product_blocked = ProductFactory.build(
		category_id=category.id,
		status=ProductStatusEnum.BLOCKED,
	)
	sku_blocked = SkuFactory.build(product_id=product_blocked.id)
	subscription = SubscriptionFactory.build(user_id=user.id, product_id=product.id)
	favorite = FavoriteFactory.build(user_id=user.id, product_id=product.id)
	favorite_blocked = FavoriteFactory.build(
		user_id=user.id, product_id=product_blocked.id
	)
	reviewer = UserFactory.build()
	reviews = [
		ReviewFactory.build(product_id=product.id, user_id=reviewer.id, rating=4),
		ReviewFactory.build(product_id=product.id, user_id=user.id, rating=5),
	]
	db_session.add_all(
		[
			user,
			reviewer,
			category,
			product,
			sku,
			product_blocked,
			sku_blocked,
			subscription,
			favorite,
			favorite_blocked,
			*reviews,
		]
	)
	await db_session.commit()
	return FavoritesData(
		user=user,
		categories=[category, category],
		products=[product, product_blocked],
		skus=[sku, sku_blocked],
		favorites=[favorite, favorite_blocked],
		subscriptions=[subscription, None],
	)


@dataclass(frozen=True, slots=True)
class SubscriptionsData:
	user: User
	product: Product
	subscription: Subscription | None


@pytest.fixture()
async def empty_subscriptions_data(db_session: AsyncSession) -> SubscriptionsData:
	user = UserFactory.build()
	category = CategoryFactory.build()
	product = ProductFactory.build(category_id=category.id)
	db_session.add_all([user, category, product])
	await db_session.commit()
	return SubscriptionsData(
		user=user,
		product=product,
		subscription=None,
	)


@pytest.fixture()
async def subscriptions_data(db_session: AsyncSession) -> SubscriptionsData:
	user = UserFactory.build()
	category = CategoryFactory.build()
	product = ProductFactory.build(category_id=category.id)
	subscription = SubscriptionFactory.build(user_id=user.id, product_id=product.id)
	db_session.add_all([user, category, product, subscription])
	await db_session.commit()
	return SubscriptionsData(
		user=user,
		product=product,
		subscription=subscription,
	)


@dataclass(frozen=True, slots=True)
class CartData:
	user: User
	categories: list[Category]
	products: list[Product]
	skus: list[Sku]
	items: list[CartItem | None]


@pytest.fixture()
async def cart_data(db_session: AsyncSession) -> CartData:
	user = UserFactory.build()
	category = CategoryFactory.build()
	products = [ProductFactory.build(category_id=category.id) for _ in range(3)]
	skus = [SkuFactory.build(product_id=product.id) for product in products]
	items = [CartItemFactory.build(user_id=user.id, sku_id=sku.id) for sku in skus]
	db_session.add_all([user, category, *products, *skus, *items])
	await db_session.commit()
	return CartData(
		user=user,
		categories=[category],
		products=products,
		skus=skus,
		items=items,
	)


@dataclass(frozen=True, slots=True)
class CollectionsData:
	categories: list[Category]
	products: list[Product]
	skus: list[Sku]
	collections: list[Collection]
	collection_products: list[CollectionProduct]


@pytest.fixture()
async def collections_data(db_session: AsyncSession) -> CollectionsData:
	category = CategoryFactory.build()
	products = [ProductFactory.build(category_id=category.id) for _ in range(3)]
	product_blocked = ProductFactory.build(
		category_id=category.id, status=ProductStatusEnum.BLOCKED
	)
	products.append(product_blocked)
	skus = [SkuFactory.build(product_id=product.id) for product in products]
	collections = [CollectionFactory.build() for _ in range(3)]
	collection_products = [
		CollectionProductFactory.build(
			product_id=product.id, collection_id=collection.id
		)
		for product in products
		for collection in collections
	]
	db_session.add_all([category, *products, *skus, *collections, *collection_products])
	await db_session.commit()
	return CollectionsData(
		categories=[category],
		products=products,
		skus=skus,
		collections=collections,
		collection_products=collection_products,
	)


@pytest.fixture()
async def blocked_collections_data(db_session: AsyncSession) -> CollectionsData:
	category = CategoryFactory.build()
	blocked_product = ProductFactory.build(
		category_id=category.id, status=ProductStatusEnum.BLOCKED
	)
	blocked_sku = SkuFactory.build(product_id=blocked_product.id)
	moderated_product = ProductFactory.build(
		category_id=category.id, status=ProductStatusEnum.MODERATED
	)
	moderated_sku = SkuFactory.build(product_id=moderated_product.id)
	collection = CollectionFactory.build()
	collection_products = [
		CollectionProductFactory.build(
			product_id=blocked_product.id, collection_id=collection.id
		),
		CollectionProductFactory.build(
			product_id=moderated_product.id, collection_id=collection.id
		),
	]
	db_session.add_all(
		[
			category,
			blocked_product,
			blocked_sku,
			moderated_product,
			moderated_sku,
			collection,
			*collection_products,
		]
	)
	await db_session.commit()
	return CollectionsData(
		categories=[category],
		products=[blocked_product, moderated_product],
		skus=[blocked_sku, moderated_sku],
		collections=[collection],
		collection_products=collection_products,
	)


@pytest.fixture()
async def out_of_stock_collections_data(db_session: AsyncSession) -> CollectionsData:
	category = CategoryFactory.build()
	product = ProductFactory.build(category_id=category.id)
	sku = SkuFactory.build(product_id=product.id, active_quantity=0)
	collection = CollectionFactory.build()
	collection_products = [
		CollectionProductFactory.build(
			product_id=product.id, collection_id=collection.id
		),
	]
	db_session.add_all([category, product, sku, collection, *collection_products])
	await db_session.commit()
	return CollectionsData(
		categories=[category],
		products=[product],
		skus=[sku],
		collections=[collection],
		collection_products=collection_products,
	)


@dataclass(frozen=True, slots=True)
class CartItemsData:
	user: User | None
	session_id: str | None
	product: Product
	sku: Sku
	items: list[CartItem]


@pytest.fixture()
async def cart_user_data(db_session: AsyncSession) -> CartItemsData:
	user = UserFactory.build()
	category = CategoryFactory.build()
	product = ProductFactory.build(category_id=category.id)
	image = ImageFactory.build(product_id=product.id)
	sku = SkuFactory.build(product_id=product.id, images=[image])
	items = [
		CartItemFactory.build(
			user_id=user.id,
			sku_id=sku.id,
			session_id=None,
			unit_price_at_add=sku.price,
		)
	]
	db_session.add_all([user, category, product, image, sku, *items])
	await db_session.commit()
	return CartItemsData(
		user=user, session_id=None, product=product, sku=sku, items=items
	)


@pytest.fixture()
async def cart_session_data(db_session: AsyncSession) -> CartItemsData:
	session_id = str(uuid.uuid4())
	category = CategoryFactory.build()
	products = [ProductFactory.build(category_id=category.id) for _ in range(3)]
	image = ImageFactory.build(product_id=products[0].id)
	sku = SkuFactory.build(product_id=products[0].id, images=[image])
	items = [
		CartItemFactory.build(
			session_id=session_id,
			sku_id=sku.id,
			user_id=None,
			unit_price_at_add=sku.price,
		)
	]
	db_session.add_all([category, *products, image, sku, *items])
	await db_session.commit()
	return CartItemsData(
		user=None,
		session_id=session_id,
		product=products[0],
		sku=sku,
		items=items,
	)


@pytest.fixture()
async def unavailable_sku_in_cart_data(db_session: AsyncSession) -> CartItemsData:
	user = UserFactory.build()
	category = CategoryFactory.build()
	product = ProductFactory.build(category_id=category.id)
	image = ImageFactory.build(product_id=product.id)
	sku = SkuFactory.build(product_id=product.id, images=[image], active_quantity=0)
	items = [CartItemFactory.build(user_id=user.id, sku_id=sku.id, session_id=None)]
	db_session.add_all([user, category, product, image, sku, *items])
	await db_session.commit()
	return CartItemsData(
		user=user, session_id=None, product=product, sku=sku, items=items
	)


@pytest.fixture()
async def cart_user_data_with_conflict(
	db_session: AsyncSession,
) -> tuple[CartItemsData, CartItemsData]:
	user = UserFactory.build()
	session_id = str(uuid.uuid4())
	category = CategoryFactory.build()
	product = ProductFactory.build(category_id=category.id)
	image = ImageFactory.build(product_id=product.id)
	sku = SkuFactory.build(product_id=product.id, images=[image], active_quantity=0)
	items_user = [
		CartItemFactory.build(
			user_id=user.id, sku_id=sku.id, session_id=None, quantity=1
		)
	]
	items_guest = [
		CartItemFactory.build(
			session_id=session_id, sku_id=sku.id, user_id=None, quantity=2
		)
	]
	db_session.add_all([user, category, product, image, sku, *items_user, *items_guest])
	await db_session.commit()
	return (
		CartItemsData(
			user=user, session_id=None, product=product, sku=sku, items=items_user
		),
		CartItemsData(
			user=None,
			session_id=session_id,
			product=product,
			sku=sku,
			items=items_guest,
		),
	)


@dataclass(frozen=True, slots=True)
class BannersData:
	banners: list[Banner]


@pytest.fixture()
async def banners_data(db_session: AsyncSession) -> BannersData:
	banners = [
		BannerFactory.build(
			start_at=datetime.now() - timedelta(days=1),
			end_at=datetime.now() + timedelta(days=1),
		)
		for _ in range(3)
	]
	db_session.add_all([*banners])
	await db_session.commit()
	return BannersData(
		banners=banners,
	)


@pytest.fixture()
async def no_active_banners_data(db_session: AsyncSession) -> BannersData:
	banners = [
		BannerFactory.build(
			start_at=datetime.now() + timedelta(days=1),
			end_at=datetime.now() + timedelta(days=2),
		)
		for _ in range(3)
	]
	db_session.add_all([*banners])
	await db_session.commit()
	return BannersData(banners=banners)
