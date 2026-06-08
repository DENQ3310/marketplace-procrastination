# US-CAT-04: блок похожих товаров

## Что сделано

Реализован блок похожих товаров 

`GET /api/v1/catalog/products/{product_id}/similar`
- **Path**: `product_id` - UUID товара.
- **Query**: `limit` - по умолчанию `10`, диапазон `1..50`.
- **Код 200**: массив **`CatalogProductCard`** (`id`, `name`, `min_price`, `has_stock`, `images`, …).
- **Код 404**: `{"code": "NOT_FOUND", "message": "..."}` — товар не найден.

Алгоритм:

1. Товары из поддерева категории товара, с условием видимости (`MODERATED`, не удалён, есть SKU с остатком).
2. Исключение текущего товара.
3. Если меньше `limit` — дополнение из поддерева родительской категории.

## Файлы

`/services/b2c/`

### API

- `api/catalog.py` — `GET /products/{product_id}/similar`

### Сервисы

- `services/product_service.py` — `get_similar_products`
- `services/schemas_builder.py` — `build_catalog_product_cards`

### CRUD

- `crud/product.py` — `get_similar_products`, `get_category_descendants`

### Схемы

- `schemas/catalog.py` — `CatalogProductCard`, `CategoryRef`, `ImageRef`

## Автотесты

```bash
make test
```

`.\services\b2c\tests\integration\catalog\test_similar.py`

## ADR

**Альтернативы:** случайная выборка; сходство по характеристикам; кэш рекомендаций.

**Выбор:** случайная выборка в SQL + fallback в родительскую категорию

**Критерии:** простота реализации; консистентность контракта с OpenAPI
