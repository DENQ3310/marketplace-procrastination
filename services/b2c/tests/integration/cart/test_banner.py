from datetime import datetime
import uuid
import pytest
from httpx import AsyncClient
from tests.integration.cart.conftest import BannersData
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.storefront.main import BannerEvent
from sqlalchemy import select


pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_active_banners_returned_sorted_by_priority(
	client: AsyncClient,
	banners_data: BannersData,
) -> None:
	response = await client.get(
		"/api/v1/catalog/banners",
	)
	assert response.status_code == 200
	body = response.json()
	assert len(body) == len(banners_data.banners)
	sorted_banners = sorted(banners_data.banners, key=lambda x: x.priority)
	assert all(
		body[i]["id"] == str(banner.id) for i, banner in enumerate(sorted_banners)
	)


async def test_no_active_banners_returns_200_empty(
	client: AsyncClient,
	no_active_banners_data: BannersData,  # noqa
) -> None:
	response = await client.get(
		"/api/v1/catalog/banners",
	)
	assert response.status_code == 200
	body = response.json()
	assert body == []


async def test_click_on_unknown_banner_returns_400(
	client: AsyncClient,
) -> None:
	response = await client.post(
		"/api/v1/catalog/banner-events",
		json={
			"events": [
				{
					"banner_id": str(uuid.uuid4()),
					"event": "click",
					"timestamp": datetime.now().isoformat(),
				}
			]
		},
	)
	assert response.status_code == 400


async def test_click_on_banner_creates_event(
	client: AsyncClient,
	banners_data: BannersData,
	db_session: AsyncSession,
) -> None:
	response = await client.post(
		"/api/v1/catalog/banner-events",
		json={
			"events": [
				{
					"banner_id": str(banners_data.banners[0].id),
					"event": "click",
					"timestamp": datetime.now().isoformat(),
				}
			]
		},
	)
	assert response.status_code == 204
	event = (
		await db_session.execute(
			select(BannerEvent).where(
				BannerEvent.banner_id == banners_data.banners[0].id
			)
		)
	).scalar_one_or_none()
	assert event is not None
	assert event.banner_id == banners_data.banners[0].id
