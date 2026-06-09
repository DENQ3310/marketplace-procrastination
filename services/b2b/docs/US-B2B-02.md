# US-B2B-02: добавление варианта товара (SKU)

## Что сделано

Добавление варианта товара (SKU) и отправка товара на модерацию при первом SKU.
Доставка событий: transactional outbox (`outbox_events`) + фоновый worker (`OUTBOX_WORKER_ENABLED`), публикация в RabbitMQ (`core/messaging`). Сообщение передаёт `X-Service-Key` в AMQP headers, а payload содержит уникальный `idempotency_key`. Повторный SKU у товара, у которого уже есть варианты, не меняет статус и не создаёт событие в outbox. Строка товара блокируется через `SELECT FOR UPDATE`, поэтому два параллельных запроса не могут одновременно определить себя как первый SKU.

### API

- **`POST /api/v1/skus`**
  - **Body**: `SkuCreate (product_id* uuid, name* string, price* int, discount, cost_price, article, images[], characteristics[])`; элемент `images` - `SkuImageCreate (url* string, ordering)`.
  - **Код 201**: `SkuResponse` (включая привязанные `images`, `characteristics`).
  - **Коды ошибок**: `404` `NOT_FOUND` (товар не найден); `403` `NOT_OWNER` (чужой товар); `403` `FORBIDDEN` (товар `HARD_BLOCKED`); `400` `INVALID_REQUEST` или `VALIDATION_ERROR`.

- **`POST /api/v1/skus/{sku_id}/images`**
  - **Body**: `ImageAttachRequest (url* string, image_id, ordering)`.
  - **Код 201**: `SkuImageResponse`.
  - **Коды ошибок**: `404` `NOT_FOUND`; `403` `NOT_OWNER` / `FORBIDDEN`; `400` `INVALID_REQUEST` или `VALIDATION_ERROR`.

## Запуск

```bash
make build up migrate
```
По адресу `localhost:8000/docs` можно найти документацию API-эндпоинтов

## Автотесты

```bash
make test
```

- `test_create_sku.py` - сценарии квеста US-B2B-02:
  - `test_first_sku_transitions_product_to_on_moderation` - первый SKU с `images[]` переводит товар в `ON_MODERATION`;
  - `test_first_sku_emits_created_event_to_moderation` - событие `CREATED` записывается в `outbox_events` со статусом `PENDING`;
  - `test_second_sku_no_state_change` - второй SKU не меняет статус `ON_MODERATION`;
  - `test_add_sku_to_hard_blocked_returns_403` - попытка добавить SKU к HARD_BLOCKED;
  - `test_missing_image_returns_400` - первый SKU без изображений;
  - `test_missing_image_url_on_attach_returns_400` - `POST /skus/{id}/images` без `url`
- `test_messaging.py` - публикация события с `X-Service-Key` в AMQP headers.

Полный набор тестов запускается командой `make test` или в job `B2B: Tests`.

## ADR

- **Альтернативы доставки `CREATED` в Moderation**:
  1. **Синхронный HTTP** `POST` в Moderation в том же запросе, что создаёт SKU - просто реализовать, но при недоступности Moderation весь `POST /skus` падает, хотя SKU в базе B2B уже создано.
  2. **Outbox-pattern** - в одной транзакции с SKU пишем строку в `outbox_events`, отдельный worker публикует в RabbitMQ; при падении брокера или Moderation API ответ продавцу остаётся код 201, событие доставляется после восстановления.
  3. **Fire-and-forget** - `asyncio.create_task`/фоновый HTTP без записи в БД: минимум кода, но при рестарте процесса или ошибке сети событие теряется, идемпотентность и повторная отправка не обеспечены.
- **Выбор**: outbox-pattern.
- **Критерии**: Moderation/брокер недоступны - продавец получает успешное создание SKU и `ON_MODERATION`, событие остаётся `PENDING` и уходит позже; сложность первой итерации - не нужна retry-логика в HTTP-обработчике, достаточно одной миграции и polling-worker, что совпадает с принципом outbox.

## Файлы

`services/b2b/`

### API эндпоинты

- `api/sku.py` - `create_sku_endpoint`, `attach_sku_image_endpoint`

### Сервисы

- `services/sku_service.py` - `create_sku`, `attach_sku_image`, `build_sku_response`
- `services/outbox_worker.py` - `run_forever`

### CRUD

- `crud/sku.py` - `create` (SKU, images, переход в `ON_MODERATION`, enqueue outbox)
- `crud/outbox.py` - `enqueue_moderation_product_created`, `process_pending_batch`, `deliver_pending_event`

### Core / инфраструктура

- `core/messaging.py` - `publish_message` (RabbitMQ)
- `core/config.py`, `.env.example` - `MODERATION_SERVICE_KEY`
- `main.py` - lifespan, запуск outbox worker

### Схемы и модели

- `schemas/sku.py` - `SkuCreate`, `SkuImageCreate`, `ImageAttachRequest`, `SkuResponse`
- `database/models/outbox.py` - `OutboxEvent`
- `database/alembic/versions/e61cbcec5a8b_message_queue_base.py` - таблица `outbox_events`

### Автотесты

- `tests/integration/test_create_sku.py`
