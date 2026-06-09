import pytest
from aio_pika import Message

from core import messaging

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
		{"event": "CREATED"},
	)

	assert exchange.message is not None
	assert exchange.message.headers == {
		"X-Service-Key": "test-moderation-service-key"
	}
	assert exchange.routing_key == "moderation.product.created"
