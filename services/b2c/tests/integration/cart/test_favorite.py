import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.catalog.base import ProductStatusEnum
from tests.factories.user import UserFactory
from tests.integration.cart.conftest import FavoritesData, auth_headers

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_add_to_favorites_returns_204(
	client: AsyncClient,
	db_session: AsyncSession,
	empty_favorites_data: FavoritesData,
) -> None:
	product = empty_favorites_data.products[0]
	response = await client.put(
		f"/api/v1/favorites/{product.id}",
		headers=await auth_headers(empty_favorites_data.user.id, db_session),
	)
	assert response.status_code == 204


async def test_repeat_add_returns_204_not_duplicate(
	client: AsyncClient,
	db_session: AsyncSession,
	favorites_data: FavoritesData,
) -> None:
	product = favorites_data.products[0]
	response = await client.put(
		f"/api/v1/favorites/{product.id}",
		headers=await auth_headers(favorites_data.user.id, db_session),
	)
	assert response.status_code == 204


async def test_blocked_product_excluded_from_list(
	client: AsyncClient,
	db_session: AsyncSession,
	favorites_data: FavoritesData,
) -> None:
	moderated_product = next(
		product
		for product in favorites_data.products
		if product.status == ProductStatusEnum.MODERATED
	)
	blocked_product = next(
		product
		for product in favorites_data.products
		if product.status == ProductStatusEnum.BLOCKED
	)
	response = await client.get(
		"/api/v1/favorites",
		headers=await auth_headers(favorites_data.user.id, db_session),
	)
	assert response.status_code == 200
	body = response.json()

	returned_product_ids = {item["id"] for item in body["items"]}
	assert str(moderated_product.id) in returned_product_ids
	assert str(blocked_product.id) not in returned_product_ids
	assert len(body["items"]) == 1
	assert body["total_count"] == 1
	assert body["limit"] == 20
	assert body["offset"] == 0
	item = body["items"][0]
	assert item["name"] == moderated_product.title
	assert item["slug"] == moderated_product.slug
	assert item["reviews_count"] == 2
	assert item["rating"] == 4.5
	assert "category" in item
	assert "seller" in item


async def test_user_id_from_query_is_ignored(
	client: AsyncClient,
	db_session: AsyncSession,
	favorites_data: FavoritesData,
) -> None:
	other_user = UserFactory.build()
	db_session.add(other_user)
	await db_session.commit()

	victim_response = await client.get(
		"/api/v1/favorites",
		headers=await auth_headers(favorites_data.user.id, db_session),
	)
	assert len(victim_response.json()["items"]) == 1

	response = await client.get(
		"/api/v1/favorites",
		params={"user_id": str(favorites_data.user.id)},
		headers=await auth_headers(other_user.id, db_session),
	)
	assert response.status_code == 200
	assert response.json()["items"] == []


async def test_delete_from_favorites_returns_204(
	client: AsyncClient,
	db_session: AsyncSession,
	favorites_data: FavoritesData,
) -> None:
	product = favorites_data.products[0]
	response = await client.delete(
		f"/api/v1/favorites/{product.id}",
		headers=await auth_headers(favorites_data.user.id, db_session),
	)
	assert response.status_code == 204


async def test_delete_non_existent_product_returns_204(
	client: AsyncClient,
	db_session: AsyncSession,
	favorites_data: FavoritesData,
) -> None:
	response = await client.delete(
		f"/api/v1/favorites/{uuid.uuid4()}",
		headers=await auth_headers(favorites_data.user.id, db_session),
	)
	assert response.status_code == 204


async def test_favorites_requires_authorization(
	client: AsyncClient,
	favorites_data: FavoritesData,
) -> None:
	product = favorites_data.products[0]
	response = await client.get("/api/v1/favorites")
	assert response.status_code == 401

	response = await client.put(f"/api/v1/favorites/{product.id}")
	assert response.status_code == 401

	response = await client.delete(f"/api/v1/favorites/{product.id}")
	assert response.status_code == 401


async def test_seller_name_is_returned(
	client: AsyncClient,
	db_session: AsyncSession,
	favorites_data: FavoritesData,
) -> None:
	response = await client.get(
		"/api/v1/favorites",
		headers=await auth_headers(favorites_data.user.id, db_session),
	)
	assert response.status_code == 200
	assert (
		response.json()["items"][0]["seller"]["display_name"]
		== favorites_data.products[0].seller.company_name
	)


async def test_add_to_favorites_unknown_product(
	client: AsyncClient,
	db_session: AsyncSession,
	favorites_data: FavoritesData,
) -> None:
	response = await client.put(
		f"/api/v1/favorites/{uuid.uuid4()}",
		headers=await auth_headers(favorites_data.user.id, db_session),
	)
	assert response.status_code == 404
	assert response.json()["code"] == "NOT_FOUND"
	assert response.json()["message"] == "Товар не найден"
