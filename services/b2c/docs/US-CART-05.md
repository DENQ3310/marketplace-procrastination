# US-CART-05: подборки товаров на главной

## Что сделано

Тематические подборки для главной страницы. 
Данные каталога читаются из локальной БД B2C, без отдельного обращения к B2B - это архитектурное решение - хранить данные в B2C и через очередь сообщений управлять обновлениями данных в сервисах.
Реализован единственный метод работы с коллекциями, представленный в спецификации OpenAPI, - `GET /api/v1/catalog/collections`

### API

- **`GET /api/v1/catalog/collections`**
  - **Код 200**: массив с товарами коллекции. В коллекцию входят только товары со статусом Moderated и с доступным количеством больше нуля.


## Запуск

```bash
make build up migrate
```

По адресу `localhost:8000/docs` — описание API.

## Автотесты

```bash
make test
```

- `tests/integration/cart/test_collections.py`
  - `test_collection_products_enriched` - подборки с карточками товаров
  - `test_blocked_products_not_in_collections` - `BLOCKED` не в `products`, `MODERATED` остаётся
  - `test_out_of_stock_products_not_in_collections` - товар не отображается, если закончился
Автотесты `collections_list_returns_metadata_without_products`, `collection_products_enriched_from_b2b`, `unavailable_products_in_unavailable_ids`, `unknown_collection_returns_404` не реализованы, поскольку реализация АПИ-методов в спецификации OpenAPI (которая считается более приоритетной по сравнению с канон флоу) отличается от самого канон флоу

## ADR

**Связь подборки с товарами**

- **Альтернативы**: массив UUID в поле подборки; отдельная таблица-связка; копия данных товара в B2C.
- **Выбор**: таблица `storefront.collection_products` (`collection_id`, `product_id`).
- **Критерии**: проще менять состав подборки без миграций JSON-массива; при удалении/блокировке товара в каталоге не нужна синхронизация копий.

## Файлы

`/services/b2c/`

### API

- `api/catalog.py` — `GET /collections`

### Сервисы

- `services/collection_service.py`

### CRUD

- `crud/collection.py`

### Схемы

- `schemas/collection.py` — `Collection`
- `schemas/catalog.py` — `CatalogProductCard`, `CategoryRef`, `ImageRef`

### Модели

- `database/models/storefront/main.py` — `Collection`, `CollectionProduct`
