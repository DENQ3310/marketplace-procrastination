import uuid

from httpx import AsyncClient
import pytest

from database.models.catalog.base import ProductStatusEnum
from tests.integration.cart.conftest import CollectionsData

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_collection_products_enriched(
	client: AsyncClient,
	collections_data: CollectionsData,
) -> None:
	response = await client.get("/api/v1/catalog/collections")
	assert response.status_code == 200
	body = response.json()
	assert len(body) == len(collections_data.collections)
	assert all(
		collection["id"]
		in [str(collection.id) for collection in collections_data.collections]
		for collection in body
	)
	products_by_id = {product.id: product for product in collections_data.products}
	categories_by_id = {
		category.id: category for category in collections_data.categories
	}
	moderated_ids = {
		str(product.id)
		for product in collections_data.products
		if product.status == ProductStatusEnum.MODERATED
	}
	for collection in body:
		for item in collection["products"]:
			assert item["id"] in moderated_ids
			db_product = products_by_id[uuid.UUID(item["id"])]
			category = categories_by_id[uuid.UUID(item["category"]["id"])]
			assert item["category"]["name"] == category.name
			assert item["seller"]["id"] == str(db_product.seller.id)
			assert item["seller"]["display_name"] == db_product.seller.company_name


async def test_blocked_products_not_in_collections(
	client: AsyncClient,
	blocked_collections_data: CollectionsData,
) -> None:
	response = await client.get("/api/v1/catalog/collections")
	assert response.status_code == 200
	body = response.json()

	collection_id = str(blocked_collections_data.collections[0].id)
	blocked_ids = {
		str(product.id)
		for product in blocked_collections_data.products
		if product.status == ProductStatusEnum.BLOCKED
	}
	moderated_ids = {
		str(product.id)
		for product in blocked_collections_data.products
		if product.status == ProductStatusEnum.MODERATED
	}

	collection = next(item for item in body if item["id"] == collection_id)
	product_ids = {item["id"] for item in collection["products"]}

	assert len(product_ids) == 1
	assert product_ids == moderated_ids
	assert product_ids.isdisjoint(blocked_ids)


async def test_out_of_stock_products_not_in_collections(
	client: AsyncClient,
	out_of_stock_collections_data: CollectionsData,  # noqa
) -> None:
	response = await client.get("/api/v1/catalog/collections")
	assert response.status_code == 200
	body = response.json()
	assert body[0]["products"] == []
