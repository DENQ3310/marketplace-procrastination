import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.outbox import OutboxEvent
from tests.integration.conftest import (
	PUBLIC_CATALOG_SERVICE_KEY_HEADERS,
	InventoryData,
)

pytestmark = pytest.mark.asyncio(loop_scope="session")


def _payload(idempotency_key: uuid.UUID, items: list[tuple[uuid.UUID, int]]) -> dict:
	return {
		"idempotency_key": str(idempotency_key),
		"items": [
			{"sku_id": str(sku_id), "quantity": quantity}
			for sku_id, quantity in items
		],
	}


async def test_reserve_all_skus_succeeds(
	client: AsyncClient,
	inventory_data: InventoryData,
	db_session: AsyncSession,
) -> None:
	first, second = inventory_data.skus
	response = await client.post(
		"/api/v1/reserve",
		headers=PUBLIC_CATALOG_SERVICE_KEY_HEADERS,
		json=_payload(uuid.uuid4(), [(first.id, 3), (second.id, 1)]),
	)

	assert response.status_code == 200
	await db_session.refresh(first)
	await db_session.refresh(second)
	assert (first.active_quantity, first.reserved_quantity) == (7, 3)
	assert (second.active_quantity, second.reserved_quantity) == (1, 1)


async def test_partial_insufficient_stock_returns_409_all_rollback(
	client: AsyncClient,
	inventory_data: InventoryData,
	db_session: AsyncSession,
) -> None:
	first, second = inventory_data.skus
	response = await client.post(
		"/api/v1/reserve",
		headers=PUBLIC_CATALOG_SERVICE_KEY_HEADERS,
		json=_payload(uuid.uuid4(), [(first.id, 3), (second.id, 3)]),
	)

	assert response.status_code == 409
	assert response.json()["code"] == "INVENTORY_CONFLICT"
	await db_session.refresh(first)
	await db_session.refresh(second)
	assert (first.active_quantity, first.reserved_quantity) == (10, 0)
	assert (second.active_quantity, second.reserved_quantity) == (2, 0)


async def test_idempotent_reserve_returns_200_without_double_deduction(
	client: AsyncClient,
	inventory_data: InventoryData,
	db_session: AsyncSession,
) -> None:
	sku = inventory_data.skus[0]
	key = uuid.uuid4()
	payload = _payload(key, [(sku.id, 4)])

	first_response = await client.post(
		"/api/v1/reserve",
		headers=PUBLIC_CATALOG_SERVICE_KEY_HEADERS,
		json=payload,
	)
	second_response = await client.post(
		"/api/v1/reserve",
		headers=PUBLIC_CATALOG_SERVICE_KEY_HEADERS,
		json=payload,
	)

	assert first_response.status_code == 200
	assert second_response.status_code == 200
	await db_session.refresh(sku)
	assert (sku.active_quantity, sku.reserved_quantity) == (6, 4)


async def test_sku_out_of_stock_event_emitted(
	client: AsyncClient,
	inventory_data: InventoryData,
	db_session: AsyncSession,
) -> None:
	sku = inventory_data.skus[1]
	response = await client.post(
		"/api/v1/reserve",
		headers=PUBLIC_CATALOG_SERVICE_KEY_HEADERS,
		json=_payload(uuid.uuid4(), [(sku.id, 2)]),
	)

	assert response.status_code == 200
	result = await db_session.execute(
		select(OutboxEvent).where(OutboxEvent.event_type == "SKU_OUT_OF_STOCK")
	)
	event = result.scalar_one()
	assert event.routing_key == "b2c.sku.out_of_stock"
	assert event.payload["payload"]["sku_id"] == str(sku.id)


async def test_unreserve_restores_quantities(
	client: AsyncClient,
	inventory_data: InventoryData,
	db_session: AsyncSession,
) -> None:
	sku = inventory_data.skus[0]
	reserve_response = await client.post(
		"/api/v1/reserve",
		headers=PUBLIC_CATALOG_SERVICE_KEY_HEADERS,
		json=_payload(uuid.uuid4(), [(sku.id, 5)]),
	)
	assert reserve_response.status_code == 200

	unreserve_response = await client.post(
		"/api/v1/unreserve",
		headers=PUBLIC_CATALOG_SERVICE_KEY_HEADERS,
		json=_payload(uuid.uuid4(), [(sku.id, 5)]),
	)

	assert unreserve_response.status_code == 200
	await db_session.refresh(sku)
	assert (sku.active_quantity, sku.reserved_quantity) == (10, 0)


async def test_reserve_missing_service_key_returns_401(client: AsyncClient) -> None:
	response = await client.post(
		"/api/v1/reserve",
		json=_payload(uuid.uuid4(), [(uuid.uuid4(), 1)]),
	)

	assert response.status_code == 401
	assert response.json()["code"] == "UNAUTHORIZED"
