# US-CAT-05: навигация по категориям

## Что сделано

Реализована навигация по категориям для B2C каталога: запросы на получение дерева категорий, деталей категории, а также генерация хлебных крошек (цепочка от корня до категории).

### API

- `GET /api/v1/catalog/categories` — плоский список `CategoryRef[]` (`id`, `name`, `parent_id`, `level`, `path`)
- `GET /api/v1/catalog/categories/tree` — дерево `CategoryTreeNode[]` (массив корней, у каждого узла `children`, `level`, `path`)
- `GET /api/v1/catalog/categories/{category_id}` — детали категории (`include_product_count`)
- `GET /api/v1/catalog/categories/{category_id}/filters` — фильтры категории
- `GET /api/v1/breadcrumbs?category_id=` | `?product_id=` — хлебные крошки

Дерево кэшируется в `cache/categories_tree.json`

## Запуск

```bash
make build up migrate
```

## Автотесты

```bash
make test
```

- `test_category_tree_returns_nested_structure`
- `test_multiple_root_categories_return_separate_tree_nodes`
- `test_breadcrumbs_return_path_from_root`
- `test_unknown_category_returns_404`
- `test_orphan_node_returns_422`
- `test_ambiguous_params_returns_400`

Тесты успешно проходят (см. джобу tests).
Перед прогоном тестов autouse-фикстура удаляет файл кэша дерева.

## ADR

- **Альтернативы**: `ltree`, adjacency list + CTE, materialized path
- **Выбор**: adjacency list (`parent_id`). Критерии: простота схемы; orphan node легко обнаружить при обходе цепочки родителей (422)
