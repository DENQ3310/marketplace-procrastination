import uuid

import pytest
from httpx import AsyncClient

from services.category_service import CATEGORIES_TREE_CACHE_FILE
from tests.integration.catalog.conftest import (
	CategoriesTreeData,
	MultipleRootCategoriesData,
	OrphanCategoryData,
)


pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(autouse=True)
def _clear_categories_tree_cache() -> None:
	if CATEGORIES_TREE_CACHE_FILE.exists():
		CATEGORIES_TREE_CACHE_FILE.unlink()
	yield
	if CATEGORIES_TREE_CACHE_FILE.exists():
		CATEGORIES_TREE_CACHE_FILE.unlink()


async def test_category_tree_returns_nested_structure(
	client: AsyncClient,
	categories_tree: CategoriesTreeData,
) -> None:
	"""
	Test that category tree returns nested structure.
	"""
	response = await client.get("/api/v1/catalog/categories/tree")
	body = response.json()

	assert response.status_code == 200
	assert body[0]["id"] == str(categories_tree.root.id)
	assert body[0]["level"] == 0
	assert body[0]["path"] == ["Электроника"]
	assert body[0]["children"][0]["id"] == str(categories_tree.child.id)
	assert body[0]["children"][0]["children"][0]["id"] == str(
		categories_tree.grandchild.id
	)
	assert body[0]["children"][0]["children"][0]["level"] == 2


async def test_multiple_root_categories_return_separate_tree_nodes(
	client: AsyncClient,
	multiple_root_categories: MultipleRootCategoriesData,
) -> None:
	response = await client.get("/api/v1/catalog/categories/tree")
	body = response.json()

	assert response.status_code == 200
	assert len(body) == 2
	root_ids = {node["id"] for node in body}
	assert root_ids == {
		str(multiple_root_categories.root_a.id),
		str(multiple_root_categories.root_b.id),
	}
	for node in body:
		assert node["level"] == 0
		assert node["children"] == []


async def test_breadcrumbs_return_path_from_root(
	client: AsyncClient,
	categories_tree: CategoriesTreeData,
) -> None:
	"""
	Test that breadcrumbs return path from root to grandchild category.
	"""
	response = await client.get(
		"/api/v1/breadcrumbs",
		params={"category_id": str(categories_tree.grandchild.id)},
	)
	body = response.json()

	assert response.status_code == 200
	assert body["data"][0]["id"] == str(categories_tree.root.id)
	assert body["data"][-1]["id"] == str(categories_tree.grandchild.id)
	assert body["data"][-1]["is_current"]
	assert body["meta"]["category_id"] == str(categories_tree.grandchild.id)


async def test_unknown_category_returns_404(client: AsyncClient) -> None:
	"""
	Test that unknown category returns 404.
	"""
	response = await client.get(f"/api/v1/catalog/categories/{uuid.uuid4()}")
	assert response.status_code == 404


async def test_orphan_node_returns_422(
	client: AsyncClient,
	orphan_category: OrphanCategoryData,
) -> None:
	"""
	Test that orphan category returns 422.
	"""
	response = await client.get(
		"/api/v1/breadcrumbs", params={"category_id": str(orphan_category.orphan.id)}
	)

	assert response.status_code == 422


async def test_ambiguous_params_returns_400(
	client: AsyncClient,
	categories_tree: CategoriesTreeData,
) -> None:
	"""
	Test that ambiguous params returns 400.
	"""
	response = await client.get(
		"/api/v1/breadcrumbs",
		params={
			"category_id": str(categories_tree.root.id),
			"product_id": str(uuid.uuid4()),
		},
	)

	assert response.status_code == 400
