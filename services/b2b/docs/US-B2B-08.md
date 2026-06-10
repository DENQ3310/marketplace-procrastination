# US-B2B-08: резервирование и снятие резерва SKU

## Реализация

Добавлены service-to-service endpoints:

- `POST /api/v1/reserve`
- `POST /api/v1/unreserve`

Оба endpoint защищены `X-Service-Key`. Запрос содержит UUID
`idempotency_key` и непустой список `{sku_id, quantity}`. Повторяющиеся SKU
агрегируются перед проверкой.

Reserve атомарно уменьшает `active_quantity` и увеличивает
`reserved_quantity`. Unreserve выполняет обратное действие. Если хотя бы одной
позиции недостаточно, возвращается `409 INVENTORY_CONFLICT`, а вся транзакция
откатывается. При переходе `active_quantity` в ноль в той же транзакции
создаётся outbox-событие `SKU_OUT_OF_STOCK` для B2C. Outbox worker публикует
события `b2c.*` с `X-Service-Key` из `B2C_SERVICE_KEY`.

## Идемпотентность

Применённые операции хранятся в `catalog.inventory_operations` с уникальностью
по `(operation, idempotency_key)`. Повтор того же payload возвращает `200` без
повторного изменения остатков. Повтор ключа с другим payload возвращает `409`.
Транзакционный advisory-lock по ключу сериализует одновременные повторы даже
тогда, когда их наборы SKU не пересекаются.

## Тесты

- `test_reserve_all_skus_succeeds`
- `test_partial_insufficient_stock_returns_409_all_rollback`
- `test_idempotent_reserve_returns_200_without_double_deduction`
- `test_sku_out_of_stock_event_emitted`
- `test_unreserve_restores_quantities`

## ADR

Рассматривались одна транзакция с `SELECT FOR UPDATE`, оптимистическая
блокировка с версией и retry, а также двухфазная запись по SKU. Выбрана одна
транзакция с пессимистической блокировкой всех SKU в стабильном порядке. Она
проще двухфазного протокола, обеспечивает all-or-nothing и предсказуемо
сериализует конкуренцию за последний остаток. Цена решения - ожидание блокировки
при высокой конкуренции; сортировка UUID снижает риск взаимных блокировок.
