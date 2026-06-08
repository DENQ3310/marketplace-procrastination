import uuid
from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.storefront.main import Banner, BannerEvent


async def get_active_banners(db: AsyncSession) -> list[Banner]:
	now = datetime.now(timezone.utc)
	query = (
		select(Banner)
		.where(
			Banner.is_active == True,  # noqa: E712
			or_(Banner.start_at.is_(None), Banner.start_at <= now),
			or_(Banner.end_at.is_(None), Banner.end_at >= now),
		)
		.order_by(Banner.priority.asc())
	)
	result = await db.execute(query)
	return list(result.scalars().all())


async def get_existing_banner_ids(
	db: AsyncSession, banner_ids: list[uuid.UUID]
) -> set[uuid.UUID]:
	if not banner_ids:
		return set()
	query = select(Banner.id).where(Banner.id.in_(banner_ids))
	result = await db.execute(query)
	return set(result.scalars().all())


async def create_banner_events(
	db: AsyncSession,
	events: list[BannerEvent],
) -> None:
	db.add_all(events)
	await db.commit()
