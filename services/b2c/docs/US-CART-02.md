# US-CART-02: подписки на изменения товара

## Что сделано

Реализация действий с подписками.
Согласно канон флоу, для MVP подписки сохраняются в БД, но автоматическая отправка уведомлений не реализуется.

### API

Используется Authorization Bearer token

- **`POST /api/v1/favorites/{product_id}/subscribe`**
  - **Path params**: `product_id`
  - **Body**: `{ "events": ["BACK_IN_STOCK", "PRICE_DROP"] }`
  - **Код 204**: подписка создана или обновлена
  - **Код 401**: не авторизован
  - **Код 404**: товар не найден
  - **Код 422**: неверные значения в `events`

- **`DELETE /api/v1/favorites/{product_id}/subscribe`**
  - **Path params**: `product_id`
  - **Код 204**: подписка удалена
  - **Код 401**: не авторизован

## Запуск

```bash
make build up migrate
```

По адресу `localhost:8000/docs` — описание API.

## Автотесты

```bash
make test
```

## ADR

- **Альтернативы**:
  - `user_id` в query/body - IDOR на список избранного
  - заголовок `X-User-Id` - подделывается клиентом
  - `user_id` из JWT после проверки подписи и активной сессии - нельзя указать чужой профиль без компрометации токена
- **Выбор**: JWT + middleware

## Файлы

### Middleware

- `middlewares/token_verification.py`

### API эндпоинты

- `api/subscriptions.py`

### Сервисы

- `services/subscription_service.py`

### CRUD

- `crud/subscription.py`

### Схемы

- `schemas/subscription.py`

### Автотесты

- `tests/integration/cart/test_subscription.py`
Тесты сделаны в соответствии с требованиями спецификации и расходятся с канон флоу:
- Тест из канон флоу `subscribe_returns_201_with_notify_on` заменён на `test_subscribe_returns_204`
- `invalid_notify_on_returns_400` заменён на `test_invalid_events_returns_422`