# US-CART-01: избранное покупателя

## Что сделано

Реализация действий с избранным и подписками

### API

Используется Authorization Bearer token

- **`GET /api/v1/favorites`**
  - **Query params**: `limit` (1-100, по умолчанию 20), `offset` (от 0)
  - **Код 200**: список избранного
  - **Код 401**: не авторизован

- **`PUT /api/v1/favorites/{product_id}`**
  - **Path params**: `product_id`
  - **Код 204**: добавлено в избранное
  - **Код 404**: товар не найден / недоступен для добавления
  - **Код 401**: не авторизован

- **`DELETE /api/v1/favorites/{product_id}`**
  - **Path params**: `product_id`
  - **Код 204**: удалено избранное
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

- `api/favorite.py`

### Сервисы

- `services/favorite_service.py`

### CRUD

- `crud/favorite.py`

### Схемы

- `schemas/catalog.py`

### Автотесты

- `tests/integration/cart/test_favorite.py`
    - Задание требует тест `add_to_favorites_returns_201`, однако в спецификации указан код 204, автотест изменён на `test_add_to_favorites_returns_204`
    - Задание требует тест `repeat_add_returns_200_not_duplicate`, однако в спецификации для повторного добавления соответствует код 204, так что проверяется сценарий `test_repeat_add_returns_204_not_duplicate`
