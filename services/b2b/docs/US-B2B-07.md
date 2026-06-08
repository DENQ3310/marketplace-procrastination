# US-B2B-07: каталог товаров для B2C (service-to-service)

## Что сделано

Публичный read-only каталог по эталону OpenAPI

## Запуск

```bash
make build up migrate
```

## Автотесты

```bash
make test
```

- `tests/integration/test_public_catalog.py`

## ADR

**Разграничение seller-view и B2C-каталога**

- **Альтернативы:** один `GET /api/v1/products` с ветвлением по `X-Service-Key` (канон B2B-7); отдельные URL `/api/v1/public/*` (OpenAPI); два view на один path.
- **Выбор:** отдельный роутер `/api/v1/public` + dependency на `X-Service-Key` - как в OpenAPI.
- **Критерии:** минимальный риск утечки `cost_price`/`reserved_quantity` в seller-режим; проще добавлять inventory/moderation endpoints без смешения auth.

## Слои

- **CRUD** (`crud/public_product.py`, `crud/images.py`, `crud/product.py`) - SQL, фильтры видимости, пакетная загрузка связанных сущностей.
- **Service** (`services/public_catalog_service.py`) - сборка DTO, `min_price`/`cover_image`, исключения домена.
- **Middleware** (`middlewares/service_key_verification.py`) - проверка `X-Service-Key` для `/api/v1/public/*`.
- **API** (`api/public_catalog.py`) - HTTP, маппинг `ProductNotFoundError` → 404.
