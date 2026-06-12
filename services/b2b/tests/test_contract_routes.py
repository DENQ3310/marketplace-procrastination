from main import app
from schemas.product import ProductCreate


def test_sku_routes_match_contract() -> None:
	paths = app.openapi()["paths"]

	assert set(paths["/api/v1/skus/{sku_id}"]) >= {"get", "patch"}
	assert "put" not in paths["/api/v1/skus/{sku_id}"]
	assert "/api/v1/products/{product_id}/skus" in paths
	assert "/api/v1/skus/product/{product_id}" not in paths


def test_product_create_allows_omitting_slug_and_images() -> None:
	assert ProductCreate.model_fields["slug"].is_required() is False
	assert ProductCreate.model_fields["images"].is_required() is False
