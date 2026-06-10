# US-B2B-07: каталог товаров для B2C (service-to-service)

## Что сделано

Реализован канонический service-to-service режим:

- `GET /api/v1/products` - каталог видимых товаров;
- `GET /api/v1/products?ids=<uuid>&ids=<uuid>` - batch-выборка видимого
  подмножества без `404` для скрытых товаров;
- авторизация через `X-Service-Key`, без seller JWT;
- видимость: только `MODERATED`, `deleted=false`, хотя бы один SKU с
  `active_quantity > 0`;
- B2C-схемы не содержат `cost_price` и `reserved_quantity`.

Существующие `/api/v1/public/products*` сохранены для обратной совместимости.

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

- **Альтернативы:** один view с ветвлением схемы по заголовку; отдельные URL
  `/api/v1/public/*`; отдельный B2C-view `GET /api/v1/products` рядом с
  seller-view `GET /api/v1/products/`.
- **Выбор:** отдельный B2C-view и отдельная response-схема, защищённые точным
  правилом `GET /api/v1/products` + `X-Service-Key`; `/public/*` оставлен как
  legacy alias.
- **Критерии:** минимальный риск утечки `cost_price`/`reserved_quantity` из-за
  ошибочной ветки сериализации; возможность независимо развивать B2C-фильтры и
  seller API.

## Слои

- **CRUD** (`crud/public_product.py`, `crud/images.py`, `crud/product.py`) - SQL, фильтры видимости, пакетная загрузка связанных сущностей.
- **Service** (`services/public_catalog_service.py`) - сборка DTO, `min_price`/`cover_image`, исключения домена.
- **Middleware** (`middlewares/service_key_verification.py`) - проверка
  `X-Service-Key` для канонического GET и `/api/v1/public/*`.
- **API** (`api/public_catalog.py`) - HTTP, маппинг `ProductNotFoundError` → 404.
