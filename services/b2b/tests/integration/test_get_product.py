import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.conftest import ViewProductData, auth_headers

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_moderated_product_returns_full_payload(
	client: AsyncClient,
	view_product_data: ViewProductData,
	db_session: AsyncSession,
) -> None:
	data = view_product_data
	headers = await auth_headers(data.owner.id, db_session)

	response = await client.get(
		f"/api/v1/products/{data.moderated_product.id}",
		headers=headers,
	)
	assert response.status_code == 200
	body = response.json()

	assert body["id"] == str(data.moderated_product.id)
	assert body["title"] == data.moderated_product.title
	assert body["status"] == "MODERATED"
	assert body["deleted"] is False
	assert body["blocked"] is False
	assert body["blocking_reason"] is None
	assert body["field_reports"] == []

	assert len(body["images"]) == 1
	assert body["images"][0]["url"] == "/s3/iphone15-front.jpg"

	assert len(body["characteristics"]) == 1
	assert body["characteristics"][0]["name"] == "Бренд"

	assert len(body["skus"]) == 1
	sku = body["skus"][0]
	assert sku["id"] == str(data.moderated_sku.id)
	assert sku["cost_price"] == data.moderated_sku.cost_price
	assert sku["reserved_quantity"] == data.moderated_sku.reserved_quantity
	assert len(sku["images"]) == 1


async def test_get_blocked_product_returns_blocking_reason_and_field_reports(
	client: AsyncClient,
	view_product_data: ViewProductData,
	db_session: AsyncSession,
) -> None:
	data = view_product_data
	headers = await auth_headers(data.owner.id, db_session)

	response = await client.get(
		f"/api/v1/products/{data.blocked_product.id}",
		headers=headers,
	)
	assert response.status_code == 200
	body = response.json()

	assert body["status"] == "BLOCKED"
	assert body["blocked"] is True
	assert body["blocking_reason"] is not None
	assert body["blocking_reason"]["id"] == str(data.blocking_reason_id)
	assert body["blocking_reason"]["title"] == "Описание не соответствует товару"
	assert body["blocking_reason"]["comment"] == "Несоответствие описания и фотографий"

	assert len(body["field_reports"]) == 2
	assert body["field_reports"][0]["field_name"] == "description"
	assert body["field_reports"][0]["comment"] == "В описании указан неверный материал"
	assert body["field_reports"][1]["field_name"] == "sku_image"
	assert body["field_reports"][1]["sku_id"] == str(data.blocked_sku.id)


async def test_get_others_product_returns_404(
	client: AsyncClient,
	view_product_data: ViewProductData,
	db_session: AsyncSession,
) -> None:
	data = view_product_data
	headers = await auth_headers(data.owner.id, db_session)

	response = await client.get(
		f"/api/v1/products/{data.other_seller_product.id}",
		headers=headers,
	)
	assert response.status_code == 404
	body = response.json()
	assert body["code"] == "NOT_FOUND"


async def test_get_nonexistent_returns_404(
	client: AsyncClient,
	view_product_data: ViewProductData,
	db_session: AsyncSession,
) -> None:
	data = view_product_data
	headers = await auth_headers(data.owner.id, db_session)

	response = await client.get(
		f"/api/v1/products/{uuid.uuid4()}",
		headers=headers,
	)
	assert response.status_code == 404
	body = response.json()
	assert body["code"] == "NOT_FOUND"
