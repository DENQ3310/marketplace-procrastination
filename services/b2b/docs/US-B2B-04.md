# US-B2B-04: удаление товара

## Что сделано

Реализован soft delete товара через:

```http
DELETE /api/v1/products/{product_id}
```

Товар физически не удаляется и сохраняет текущий статус. В одной транзакции:

1. Поле `deleted` устанавливается в `true`.
2. В outbox создаётся событие `PRODUCT_DELETED` для Moderation.
3. В outbox создаётся событие `PRODUCT_DELETED` для B2C со всеми `sku_ids`.

Удалённый товар не возвращается стандартным списком продавца и уже исключается
из публичного B2C-каталога фильтром `deleted=false`.

## API

- **`DELETE /api/v1/products/{product_id}`**
  - **Auth**: Bearer JWT, владелец определяется только по JWT.
  - **Код 200**: `{"message": "Product deleted successfully"}`.
  - **Код 400**: `ALREADY_DELETED` при повторном удалении.
  - **Код 403**: `NOT_OWNER` для чужого товара, `FORBIDDEN` для
    `HARD_BLOCKED`.
  - **Код 404**: `NOT_FOUND` для несуществующего товара.

Все ошибки возвращаются в формате `{code, message}`.

## События

Оба события имеют общую форму:

```json
{
  "event_type": "PRODUCT_DELETED",
  "idempotency_key": "uuid",
  "occurred_at": "2026-06-10T00:00:00Z",
  "payload": {}
}
```

Moderation получает `product_id` и `seller_id` по routing key
`moderation.product.deleted`. B2C получает `product_id` и `sku_ids` по routing
key `b2c.product.deleted`.

## Тесты

В `tests/integration/test_delete_product.py` покрыты:

- `test_delete_sets_deleted_true`;
- `test_delete_emits_event_to_moderation`;
- `test_delete_emits_product_deleted_to_b2c`;
- `test_delete_already_deleted_returns_400`;
- `test_deleted_product_not_in_seller_list`;
- `test_delete_others_product_returns_403`.

## ADR

Рассматривались два синхронных запроса, смешанная схема с синхронным вызовом
Moderation и outbox для B2C, а также outbox для обоих событий. Выбран единый
transactional outbox: флаг удаления и оба события фиксируются одной транзакцией,
поэтому недоступность одного потребителя не создаёт частично выполненное
удаление. Этот вариант требует фонового worker, который уже используется
сервисом, но обеспечивает повторную доставку и согласованность данных.

