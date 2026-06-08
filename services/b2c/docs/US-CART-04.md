# US-CART-04: баннеры на главной

## Что сделано

Получение баннеров

### API

- **`GET /api/v1/catalog/banners`**
  - **Код 200**: массив `Banner` (`id`, `title`, `image_url`, `link`, `ordering`, `active_from`, `active_to`)
  - Только `is_active=true` и текущее время в окне `start_at` / `end_at` 
  - Сортировка по `ordering`
  - Авторизация не требуется

- **`POST /api/v1/catalog/banner-events`**
Реализован, хотя нет в спецификации OpenAPI, но есть в канон флоу.
  - **Body**: `{ "events": [{ "banner_id": uuid, "event": "impression" | "click", "timestamp": datetime }] }`
  - **Код 204**: события записаны
  - **Код 400**: `BANNER_NOT_FOUND` — неизвестный `banner_id`; `EMPTY_EVENTS` — пустой список на уровне сервиса

## Запуск

```bash
make build up migrate
```

По адресу `localhost:8000/docs` — описание API.

## Автотесты

```bash
make test
```

- `tests/integration/cart/test_banner.py`
  - `test_active_banners_returned_sorted_by_priority` - активные баннеры, порядок по `ordering`
  - `test_no_active_banners_returns_200_empty` - нет активных баннеров - `200` и `[]`
  - `test_click_on_unknown_banner_returns_400` - неизвестный баннер
  - `test_click_on_banner_creates_event` - клик пишется в `banner_events`

## ADR

**Хранение аналитики кликов и показов**

- **Альтернативы**: строка в реляционную таблицу на каждое событие; батч в очередь/файл с отложенной записью; внешняя аналитика.
- **Выбор**: таблица `storefront.banner_events`, вставка батчем из тела `POST /banner-events`.
- **Критерии**: при высоком трафике главной проще масштабировать запись (индексы, партиции, архив), чем синхронные внешние вызовы; Отчёты - обычные SQL-агрегации по `banner_id` и `event`.

## Файлы
`/services/b2c/`

### API

- `api/catalog.py`

### Сервисы

- `services/banner_service.py`

### CRUD

- `crud/banner.py`

### Схемы

- `schemas/banner.py`

### Модели

- `database/models/storefront/main.py` - `Banner`, `BannerEvent`

### Исключения

- `exceptions/banner.py`
