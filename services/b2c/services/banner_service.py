import uuid

from sqlalchemy.ext.asyncio import AsyncSession

import crud.banner as banner_crud
from database.models.storefront.main import BannerEvent
from exceptions.banner import BannerNotFoundError, EmptyEventsError
from schemas.banner import Banner, BannerEventsRequest


async def get_active_banners(db: AsyncSession) -> list[Banner]:
	banners = await banner_crud.get_active_banners(db)
	return [
		Banner(
			id=banner.id,
			title=banner.title,
			image_url=banner.image_url,
			link=banner.link,
			ordering=banner.priority,
			active_from=banner.start_at,
			active_to=banner.end_at,
		)
		for banner in banners
	]


async def record_banner_events(
	db: AsyncSession,
	body: BannerEventsRequest,
	user_id: uuid.UUID | None = None,
) -> None:
	if not body.events:
		raise EmptyEventsError("Events list must not be empty")

	banner_ids = list({event.banner_id for event in body.events})
	existing_ids = await banner_crud.get_existing_banner_ids(db, banner_ids)
	missing_ids = set(banner_ids) - existing_ids
	if missing_ids:
		raise BannerNotFoundError(f"Banner not found: {missing_ids.pop()}")

	rows = [
		BannerEvent(
			banner_id=event.banner_id,
			user_id=user_id,
			event=event.event,
			timestamp=event.timestamp,
		)
		for event in body.events
	]
	await banner_crud.create_banner_events(db, rows)
