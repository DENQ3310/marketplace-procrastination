# US-ORD-01: оформление заказа (checkout)

## Что сделано

Реализован checkout для авторизованного покупателя: создание заказа из корзины, атомарный резерв остатков SKU, идемпотентность повторных запросов, заглушка оплаты (заказ сразу в статусе `PAID`).

Данные берутся только из локальной БД B2C (корзина, каталог, адреса, способы оплаты) — без проксирования в B2B.

### API

- **`POST /api/v1/orders`**
  - **Заголовки**: `Authorization: Bearer <JWT>`, `Idempotency-Key: <UUID>`
  - **Body** (`OrderCreateRequest`):
    - `address_id` (uuid) — адрес доставки покупателя
    - `payment_method_id` (uuid) — способ оплаты покупателя
    - `comment` (string, optional, max 1000)
    - `items_snapshot` (optional) — снимок позиций корзины для сверки перед оформлением
  - **Код 201**: `OrderResponse` — созданный или ранее созданный (идемпотентный) заказ
  - **Код 400**: пустая корзина; невалидный `Idempotency-Key`
  - **Код 401**: нет или невалидный JWT
  - **Код 404**: адрес или способ оплаты не найден / не принадлежит пользователю
  - **Код 409**:
    - `IDEMPOTENCY_CONFLICT` — тот же `Idempotency-Key`, но другое тело запроса
    - `RESERVE_FAILED` — не удалось зарезервировать одну или несколько позиций (`details[]`: `sku_id`, `requested`, `reason`, опционально `available`)
  - **Код 422**: корзина не прошла валидацию (`VALIDATION_ERROR`, в `details` — `CartValidationResponse`)

## Запуск

```bash
make build up migrate
```

По адресу `localhost:8000/docs` — описание API

## Автотесты

```bash
uv run python -m pytest -q tests/integration/order/test_checkout.py
```

Требуемый в квесте тест `b2b_unavailable_returns_503` не реализован: Данные каталога читаются из локальной БД B2C, без отдельного обращения к B2B - это архитектурное решение - хранить данные в B2C и через очередь сообщений управлять обновлениями данных в сервисах.


## ADR

- **Альтернативы**: уникальный индекс на `orders.idempotency_key`; отдельная таблица-кэш ключей; Redis.
- **Выбор**: уникальный индекс на `orders.idempotency_key` + `idempotency_request_hash` в той же строке.
- **Критерии**:
  - **Race condition**: unique в PostgreSQL гарантирует ровно один заказ на ключ; проигравший запрос корректно завершается через `IntegrityError` и возврат существующего заказа. Для US-ORD-01 этого достаточно; отдельная таблица/Redis имеет смысл, если станет узким местом дублирующая работа до insert.
  - **Сложность реализации**: минимальные изменения в уже существующей модели заказа, без Redis и без второй сущности с синхронизацией статусов.

## Файлы

### Middleware

- `middlewares/token_verification.py`

### API

- `api/orders.py`

### Сервисы

- `services/order_service.py`

### CRUD

- `crud/order.py`
- `crud/address.py`, `crud/payment_method.py`

### Схемы

- `schemas/order.py`
- `schemas/address.py`, `schemas/payment_method.py`

### Модели

- `database/models/orders/order.py`, `order_item.py`
- `database/models/personal/address.py`, `payment_method.py`

### Исключения

- `exceptions/order.py`


### Автотесты

- `tests/integration/order/test_checkout.py`
