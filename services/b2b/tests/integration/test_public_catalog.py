import uuid

import pytest
from httpx import AsyncClient

from tests.integration.conftest import (
	PUBLIC_CATALOG_SERVICE_KEY_HEADERS,
	PublicCatalogData,
)

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_catalog_returns_moderated_in_stock_products(
	client: AsyncClient,
	public_catalog_data: PublicCatalogData,
) -> None:
	response = await client.get(
		"/api/v1/public/products", headers=PUBLIC_CATALOG_SERVICE_KEY_HEADERS
	)
	assert response.status_code == 200
	body = response.json()

	ids = {item["id"] for item in body["items"]}
	assert str(public_catalog_data.visible_product.id) in ids
	assert str(public_catalog_data.hard_blocked_product.id) not in ids
	assert str(public_catalog_data.out_of_stock_product.id) not in ids
	assert str(public_catalog_data.on_moderation_product.id) not in ids

	for item in body["items"]:
		assert item["status"] == "MODERATED"
		assert item["min_price"] > 0


async def test_catalog_excludes_hard_blocked(
	client: AsyncClient,
	public_catalog_data: PublicCatalogData,
) -> None:
	response = await client.get(
		"/api/v1/public/products", headers=PUBLIC_CATALOG_SERVICE_KEY_HEADERS
	)
	assert response.status_code == 200
	ids = {item["id"] for item in response.json()["items"]}
	assert str(public_catalog_data.hard_blocked_product.id) not in ids


async def test_catalog_missing_service_key_returns_401(client: AsyncClient) -> None:
	list_response = await client.get("/api/v1/public/products")
	assert list_response.status_code == 401
	assert list_response.json()["code"] == "UNAUTHORIZED"

	batch_response = await client.post(
		"/api/v1/public/products/batch",
		json={"product_ids": [str(uuid.uuid4())]},
	)
	assert batch_response.status_code == 401


async def test_catalog_response_has_no_cost_price(
	client: AsyncClient,
	public_catalog_data: PublicCatalogData,
) -> None:
	response = await client.post(
		"/api/v1/public/products/batch",
		headers=PUBLIC_CATALOG_SERVICE_KEY_HEADERS,
		json={"product_ids": [str(public_catalog_data.visible_product.id)]},
	)
	assert response.status_code == 200
	body = response.json()
	assert len(body) == 1

	assert "cost_price" not in body
	assert "cost_price" not in body[0]
	assert "reserved_quantity" not in body
	assert "reserved_quantity" not in body[0]


async def test_batch_ids_returns_visible_subset(
	client: AsyncClient,
	public_catalog_data: PublicCatalogData,
) -> None:
	data = public_catalog_data
	response = await client.post(
		"/api/v1/public/products/batch",
		headers=PUBLIC_CATALOG_SERVICE_KEY_HEADERS,
		json={
			"product_ids": [
				str(data.visible_product.id),
				str(data.hard_blocked_product.id),
				str(data.out_of_stock_product.id),
			]
		},
	)
	assert response.status_code == 200
	body = response.json()
	returned_ids = {item["id"] for item in body}
	assert returned_ids == {str(data.visible_product.id)}
