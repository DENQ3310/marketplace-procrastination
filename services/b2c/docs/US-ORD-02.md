# US-ORD-02: просмотр и отслеживание заказов

## Что сделано

Реализован просмотр списка заказов пользователя с пагинацией и фильтром по статусу, а также просмотр конкретного заказа

### API

- **`GET /api/v1/orders`**
  - **Заголовки**: `Authorization`
  - **Query**:
    - `limit` (int, optional, default 20, 1..100)
    - `offset` (int, optional, default 0, >= 0)
    - `status` (OrderStatusEnum, optional)
  - **Код 200**: `PaginatedOrders` c полями `items`, `total_count`, `limit`, `offset`
  - **Код 401**: нет или невалидный JWT

- **`GET /api/v1/orders/{order_id}`**
  - **Заголовки**: `Authorization`
  - **Path**:
    - `order_id` (uuid) - идентификатор заказа
  - **Код 200**: `OrderResponse`
  - **Код 401**: нет или невалидный JWT
  - **Код 404**: заказ не найден или не принадлежит пользователю (IDOR-защита, всегда 404)

## Запуск

```bash
make build up migrate
```

По адресу `localhost:8000/docs` — описание API

## Автотесты

```bash
uv run python -m pytest -q tests/integration/order/test_get_orders.py
```

## ADR

Рассмотрены три способа защиты от IDOR при получении заказа по ID: `filter(user=request.user).get(id=...)`, `get(id=...)` с отдельной проверкой владельца, и ограничение доступа через permission class/scope.  
Подход с отдельной проверкой владельца после `get(id=...)` хуже по читаемости и даёт больше ветвлений, а также требует аккуратно выравнивать поведение для «не найден» и «чужой заказ», чтобы не допустить утечки через разные ответы.  
Подход через permission class/scope может быть удобен для общих правил, но в этом кейсе усложняет трассировку SQL-фильтра ownership и при неожиданном отсутствии заказа всё равно требует аккуратной унификации ответа.  
Выбор: `filter(user=request.user).get(id=...)` (в проекте - эквивалентный SQL-фильтр `where(id=..., buyer_id=...)`) как наиболее читаемый и безопасный вариант по критериям читаемости кода и предсказуемого поведения при отсутствии заказа (всегда единый 404).

## Файлы

### API

- `api/orders.py`

### Сервисы

- `services/order_service.py`

### CRUD

- `crud/order.py`

### Схемы

- `schemas/order.py`

### Автотесты

- `tests/integration/order/test_get_orders.py`
