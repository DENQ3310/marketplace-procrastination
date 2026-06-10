# US-B2B-05: просмотр карточки товара и причин блокировки

## Что сделано

Реализован seller-view `GET /api/v1/products/{product_id}`: `blocking_reason` и `field_reports` отдаются из локальной БД B2B (поля заполняются при приёме события от Moderation через очередь - handler вне scope этого квеста).

### API

- **`GET /api/v1/products/{product_id}`**
  - **Auth**: Bearer JWT (`seller_id` из claims, не из query).
  - **Код 200**: `ProductDetailResponse` - полная карточка продавца.
  - **Код 404**: `NOT_FOUND` - товар не найден или принадлежит другому продавцу.

## Запуск

```bash
make build up migrate
```

## Автотесты

```bash
make test
```

- `test_get_product.py`

Дополнительно `test_get_product_supports_all_five_statuses` проверяет доступность
карточки в состояниях `CREATED`, `ON_MODERATION`, `MODERATED`, `BLOCKED` и
`HARD_BLOCKED`. `test_get_product_preserves_zero_cost_price` защищает полный
seller-payload от преобразования фактического `cost_price=0` в `null`.

## ADR

**Вопрос:** откуда `GET /api/v1/products/{id}` берёт `blocking_reason` и `field_reports` для продавца?

- **Альтернативы:**
  1. **Синхронный запрос в Moderation при каждом GET** - B2B по `product_id` тянет актуальные замечания из чужого API; карточка зависит от доступности Moderation и добавляет latency.
  2. **Общая БД** - Moderation и B2B читают одну схему; проще для read, но нарушает границы сервисов и усложняет независимый деплой.
  3. **Очередь + локальная БД B2B** - Moderation публикует результат (`MODERATED` / `BLOCKED` с `blocking_reason`, `field_reports`) в брокер; B2B принимает событие (handler B2B-9, out of scope этого квеста) и денормализует данные в `catalog.products` (`blocked_reason_id`, `blocking_reason_title`, `moderator_comment`, `field_reports`). GET только читает свою БД.

- **Выбор:** вариант 3 - в духе уже принятого в проекте обмена через outbox/RabbitMQ (B2B - Moderation при `CREATED`/`EDITED`): каждый сервис хранит у себя то, что нужно для своих сценариев. US-B2B-05 реализует чтение из локальной БД; запись при входящем событии - отдельный квест.

- **Критерии:**
  - **Автономность и отказоустойчивость** - кабинет продавца показывает причину блокировки без live-зависимости от Moderation.
  - **Согласованность архитектуры** - асинхронный контракт между сервисами, без shared DB и без лишних межсервисных GET на hot path.

## Файлы

- `database/models/catalog/base.py` - `blocking_reason_title`, `field_reports`
- `database/alembic/versions/7bea7d8e6d06_add_blocking_reasons.py`
- `schemas/product.py` - `ProductDetailResponse`, `BlockingReason`, `FieldReport`
- `crud/product.py` - `get_product_characteristics`
- `services/product_service.py` - `build_product_detail_response`, `get_product_for_seller`
- `api/products.py`
- `tests/integration/test_get_product.py`

## ADR: seller-view и service-to-service view

Рассматривались единый endpoint с переключением ответа по auth-заголовку, два
отдельных endpoint и общий permission-класс с динамической схемой ответа.
Выбраны отдельные view: seller-view `GET /api/v1/products/{id}` и существующий
service-to-service каталог `/api/v1/public/products*`. Это делает режим доступа
явным в маршруте и модели ответа, поэтому код проще читать и тестировать.
Главный критерий выбора - снижение риска утечки seller-only полей
`cost_price`, `reserved_quantity`, `blocking_reason` и `field_reports` в B2C.
