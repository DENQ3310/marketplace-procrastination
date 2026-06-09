import json

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message

from core.config import settings


def _rabbitmq_url() -> str:
	return (
		f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}"
		f"@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
	)


async def publish_message(routing_key: str, payload: dict) -> None:
	body = json.dumps(payload).encode("utf-8")
	headers = {}
	if routing_key.startswith("moderation.") and settings.MODERATION_SERVICE_KEY:
		headers["X-Service-Key"] = settings.MODERATION_SERVICE_KEY
	connection = await aio_pika.connect_robust(_rabbitmq_url())
	async with connection:
		channel = await connection.channel()
		exchange = await channel.declare_exchange(
			settings.RABBITMQ_EXCHANGE,
			ExchangeType.TOPIC,
			durable=True,
		)
		await exchange.publish(
			Message(
				body=body,
				delivery_mode=DeliveryMode.PERSISTENT,
				headers=headers,
			),
			routing_key=routing_key,
		)
