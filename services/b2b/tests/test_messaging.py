import uuid

import pytest
from aio_pika import Message

from core import messaging
from crud.outbox import (
	build_b2c_product_deleted_payload,
	build_moderation_product_event_payload,
)

pytestmark = pytest.mark.asyncio


class FakeExchange:
	def __init__(self) -> None:
		self.message: Message | None = None
		self.routing_key: str | None = None

	async def publish(self, message: Message, routing_key: str) -> None:
		self.message = message
		self.routing_key = routing_key


class FakeChannel:
	def __init__(self, exchange: FakeExchange) -> None:
		self.exchange = exchange

	async def declare_exchange(
		self,
		*_args: object,
		**_kwargs: object,
	) -> FakeExchange:
		return self.exchange


class FakeConnection:
	def __init__(self, exchange: FakeExchange) -> None:
		self.exchange = exchange

	async def __aenter__(self) -> "FakeConnection":
		return self

	async def __aexit__(self, *_args: object) -> None:
		return None

	async def channel(self) -> FakeChannel:
		return FakeChannel(self.exchange)


async def test_moderation_event_payload_matches_contract() -> None:
	product_id = uuid.uuid4()
	seller_id = uuid.uuid4()
	idempotency_key = uuid.uuid4()

	payload = build_moderation_product_event_payload(
		product_id,
		seller_id,
		idempotency_key,
		event="EDITED",
	)

	assert set(payload) == {
		"event_type",
		"idempotency_key",
		"occurred_at",
		"payload",
	}
	assert payload["event_type"] == "PRODUCT_EDITED"
	assert payload["idempotency_key"] == str(idempotency_key)
	assert payload["occurred_at"].endswith("Z")
	assert payload["payload"] == {
		"product_id": str(product_id),
		"seller_id": str(seller_id),
	}


async def test_b2c_product_deleted_payload_contains_sku_ids() -> None:
	product_id = uuid.uuid4()
	sku_ids = [uuid.uuid4(), uuid.uuid4()]
	idempotency_key = uuid.uuid4()

	payload = build_b2c_product_deleted_payload(
		product_id,
		sku_ids,
		idempotency_key,
	)

	assert payload["event_type"] == "PRODUCT_DELETED"
	assert payload["idempotency_key"] == str(idempotency_key)
	assert payload["occurred_at"].endswith("Z")
	assert payload["payload"] == {
		"product_id": str(product_id),
		"sku_ids": [str(sku_id) for sku_id in sku_ids],
	}


async def test_moderation_event_has_service_key_header(
	monkeypatch: pytest.MonkeyPatch,
) -> None:
	exchange = FakeExchange()

	async def fake_connect_robust(_url: str) -> FakeConnection:
		return FakeConnection(exchange)

	monkeypatch.setattr(messaging.aio_pika, "connect_robust", fake_connect_robust)
	monkeypatch.setattr(
		messaging.settings,
		"MODERATION_SERVICE_KEY",
		"test-moderation-service-key",
	)

	await messaging.publish_message(
		"moderation.product.created",
		{
			"event_type": "PRODUCT_CREATED",
			"idempotency_key": "event-id",
			"occurred_at": "2026-06-10T00:00:00Z",
			"payload": {"product_id": "product-id", "seller_id": "seller-id"},
		},
	)

	assert exchange.message is not None
	assert exchange.message.headers == {
		"X-Service-Key": "test-moderation-service-key"
	}
	assert exchange.routing_key == "moderation.product.created"
