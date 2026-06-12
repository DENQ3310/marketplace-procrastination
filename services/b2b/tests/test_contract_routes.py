from main import app
from schemas.product import ProductCreate


def test_edit_routes_use_patch_only() -> None:
	paths = app.openapi()["paths"]

	for path in (
		"/api/v1/products/{product_id}",
		"/api/v1/skus/{sku_id}",
	):
		assert "patch" in paths[path]
		assert "put" not in paths[path]


def test_sku_list_route_matches_contract() -> None:
	paths = app.openapi()["paths"]

	assert "/api/v1/products/{product_id}/skus" in paths
	assert "/api/v1/skus/product/{product_id}" not in paths


def test_delete_sku_route_matches_contract() -> None:
	paths = app.openapi()["paths"]

	assert "delete" in paths["/api/v1/skus/{sku_id}"]


def test_product_create_allows_omitting_slug_and_images() -> None:
	assert ProductCreate.model_fields["slug"].is_required() is False
	assert ProductCreate.model_fields["images"].is_required() is False


def test_inventory_routes_match_contract() -> None:
	paths = app.openapi()["paths"]

	assert "/api/v1/inventory/reserve" in paths
	assert "/api/v1/inventory/unreserve" in paths
	assert "/api/v1/reserve" not in paths
	assert "/api/v1/unreserve" not in paths
