import asyncio

from crud import outbox as outbox_crud
from core.config import settings
from core.messaging import publish_message


async def run_forever() -> None:
	while True:
		await outbox_crud.process_pending_batch(publish_message)
		await asyncio.sleep(settings.OUTBOX_POLL_INTERVAL_SECONDS)
