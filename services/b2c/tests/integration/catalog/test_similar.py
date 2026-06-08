import uuid

import pytest
from httpx import AsyncClient

from tests.integration.catalog.conftest import SimilarProductsData

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_similar_returns_up_to_8_from_same_category(
	client: AsyncClient,
	similar_products_data: SimilarProductsData,
) -> None:
	base = similar_products_data.base_product
	candidate_ids = {
		str(product.id) for product in similar_products_data.similar_products
	}
	other_ids = {str(product.id) for product in similar_products_data.other_products}

	response = await client.get(
		f"/api/v1/catalog/products/{base.id}/similar",
		params={"limit": 8},
	)

	assert response.status_code == 200
	body = response.json()
	ids = [item["id"] for item in body]

	assert len(body) == 8
	assert str(base.id) not in ids
	assert set(ids).issubset(candidate_ids)
	assert set(ids).isdisjoint(other_ids)
	for item in body:
		assert "name" in item
		assert "min_price" in item
		assert "has_stock" in item
		assert "images" in item
		assert item["has_stock"] is True


async def test_empty_category_returns_200_empty_list(
	client: AsyncClient,
	one_product_category: SimilarProductsData,
) -> None:
	base = one_product_category.base_product
	response = await client.get(
		f"/api/v1/catalog/products/{base.id}/similar",
	)
	assert response.status_code == 200
	assert response.json() == []


async def test_unknown_product_returns_404(
	client: AsyncClient,
	similar_products_data: SimilarProductsData,  # noqa
) -> None:
	response = await client.get(
		f"/api/v1/catalog/products/{uuid.uuid4()}/similar",
	)
	assert response.status_code == 404
	assert response.json()["code"] == "NOT_FOUND"
