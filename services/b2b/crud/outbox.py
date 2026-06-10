import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import SessionLocal
from database.models.outbox import OutboxEvent, OutboxEventStatus

PublishFn = Callable[[str, dict], Awaitable[None]]

MODERATION_EVENT_TYPES = {
	"CREATED": "PRODUCT_CREATED",
	"EDITED": "PRODUCT_EDITED",
}
MODERATION_ROUTING_KEYS = {
	"CREATED": "moderation.product.created",
	"EDITED": "moderation.product.edited",
}


def build_moderation_product_event_payload(
	product_id: UUID,
	seller_id: UUID,
	idempotency_key: UUID,
	event: str = "CREATED",
) -> dict:
	occurred_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
	event_type = MODERATION_EVENT_TYPES[event]
	return {
		"event_type": event_type,
		"idempotency_key": str(idempotency_key),
		"occurred_at": occurred_at,
		"payload": {
			"product_id": str(product_id),
			"seller_id": str(seller_id),
		},
	}


async def enqueue_moderation_product_created(
	db: AsyncSession,
	product_id: UUID,
	seller_id: UUID,
	event: str = "CREATED",
) -> OutboxEvent:
	idempotency_key = uuid.uuid4()
	event_type = MODERATION_EVENT_TYPES[event]
	routing_key = MODERATION_ROUTING_KEYS[event]
	payload = build_moderation_product_event_payload(
		product_id=product_id,
		seller_id=seller_id,
		idempotency_key=idempotency_key,
		event=event,
	)
	outbox_event = OutboxEvent(
		idempotency_key=idempotency_key,
		event_type=event_type,
		routing_key=routing_key,
		payload=payload,
		status=OutboxEventStatus.PENDING,
	)
	db.add(outbox_event)
	await db.flush()
	return outbox_event


async def fetch_pending_events(db: AsyncSession, limit: int = 50) -> list[OutboxEvent]:
	result = await db.execute(
		select(OutboxEvent)
		.where(OutboxEvent.status == OutboxEventStatus.PENDING)
		.order_by(OutboxEvent.created_at)
		.limit(limit)
	)
	return list(result.scalars().all())


async def get_pending_event_by_id(
	db: AsyncSession, event_id: UUID
) -> OutboxEvent | None:
	event = await db.get(OutboxEvent, event_id)
	if event is None or event.status != OutboxEventStatus.PENDING:
		return None
	return event


async def mark_event_sent(db: AsyncSession, event: OutboxEvent) -> None:
	event.status = OutboxEventStatus.SENT
	event.sent_at = datetime.now(timezone.utc)
	db.add(event)
	await db.commit()


async def deliver_pending_event(
	db: AsyncSession,
	event_id: UUID,
	publish: PublishFn,
) -> bool:
	db_event = await get_pending_event_by_id(db, event_id)
	if db_event is None:
		return False
	try:
		await publish(db_event.routing_key, db_event.payload)
		await mark_event_sent(db, db_event)
		return True
	except Exception:  # noqa
		await db.rollback()
		return False


async def process_pending_batch(publish: PublishFn, limit: int = 50) -> int:
	processed = 0
	async with SessionLocal() as db:
		events = await fetch_pending_events(db, limit=limit)

	for event in events:
		async with SessionLocal() as db:
			if await deliver_pending_event(db, event.id, publish):
				processed += 1
	return processed
