# US-CART-03: корзина покупателя

## Что сделано

Реализация корзины (гостевой и пользовательской).
Данные каталога читаются из локальной БД B2C, без отдельного обращения к B2B - это архитектурное решение - хранить данные в B2C и через очередь сообщений управлять обновлениями данных в сервисах.

### API

- **`GET /api/v1/cart`**
  - **Код 200**: `CartResponse` (`items`, `items_count`, `subtotal`, `is_valid`, `updated_at`)
  - **Код 400**: нет identity / невалидный `X-Session-Id`
  - **Код 401**: невалидный или отозванный JWT

- **`DELETE /api/v1/cart`**
  - **Код 204**: корзина очищена

- **`POST /api/v1/cart/items`**
  - **Body**: `{ "sku_id": uuid, "quantity": int }`
  - **Код 200**: обновлённая корзина
  - **Код 404**: SKU не найден или недоступен для добавления

- **`PATCH /api/v1/cart/items/{sku_id}`**
  - **Body**: `{ "quantity": int }`
  - **Код 200**: обновлённая корзина
  - **Код 404**: SKU не найден или недоступен для добавления

- **`DELETE /api/v1/cart/items/{sku_id}`**
  - **Код 200**: корзина без удалённой позиции

- **`POST /api/v1/cart/validate`**
  - **Код 200**: `CartValidationResponse` (`is_valid`, `cart`, `issues[]`)
  - Типы ошибок валидации: `OUT_OF_STOCK`, `PRODUCT_BLOCKED`, `PRODUCT_DELETED`, `QUANTITY_REDUCED`

- **`POST /api/v1/cart/merge`**
  - **Заголовки**: Bearer + `X-Session-Id`
  - **Код 200**: слитая пользовательская корзина
  - **Код 401**: нет auth или session

## Запуск

```bash
make build up migrate
```

По адресу `localhost:8000/docs` — описание API.

## Автотесты

```bash
make test
```

- `tests/integration/cart/test_cart.py`
  - `test_test_get_cart_enriched_with_b2b_data_user` / `_session` - обогащение при GET
  - `test_add_sku_increments_quantity_if_already_in_cart` - добавление в корзину товара, который уже есть в ней
  - `test_update_cart_item_quantity_returns_updated_cart` - изменения количества товара в корзине
  - `test_unavailable_sku_shown_with_reason`, `test_validate_reports_price_changed`,  `test_success_cart_validation` - тесты валидации
  - `test_guest_cart_merged_on_login` - merge гостевой и пользовательской корзин с конфликтом
  - `test_merge_without_auth_returns_401` - merge корзин без авторизации
  - `test_clear_cart_returns_204`, `test_delete_cart_item_returns_updated_cart` - удаление товаров из корзины

## ADR

**Идентификация гостевой корзины**

- **Альтернативы**: заголовок `X-Session-Id`; cookie `cart_session`; отдельный guest JWT.
- **Выбор**: `X-Session-Id` (UUID на клиенте).
- **Критерии**: удобно для мобильных клиентов и быстро (явная передача, без привязки к cookie); риск подделки ID выше, чем у server-side session cookie, но для MVP приемлемо оставить UUID v4, кроме того, в гостевой корзине нет чувствительных данных.
- **Авторизованный доступ**: JWT + проверка сессии в БД (как избранное), без `X-User-Id`.


## Файлы

### Middleware

- `middlewares/token_verification.py`

### API

- `api/cart.py`

### Сервисы

- `services/cart_service.py`
- `services/auth_service.py` - merge при login

### CRUD

- `crud/cart.py`

### Схемы

- `schemas/cart.py`

### Модели

- `database/models/cart/item.py`

### Исключения

- `exceptions/cart.py`, `exceptions/sku.py`
