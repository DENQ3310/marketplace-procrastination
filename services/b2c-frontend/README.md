# B2C Frontend - Marketplace

Фронтенд приложение для маркетплейса на React с использованием Vite.

## Технологии

- **React 19** - UI библиотека
- **React Router DOM** - роутинг
- **Zustand** - управление состоянием
- **Axios** - HTTP клиент
- **Vite** - сборщик и dev сервер

## Структура проекта

```
src/
├── api/                    # API клиенты
│   ├── client.js          # Настроенный axios instance
│   ├── categories.js      # API для категорий
│   ├── products.js        # API для продуктов
│   ├── cart.js            # API для корзины
│   └── index.js           # Экспорты
├── components/
│   ├── common/            # Переиспользуемые компоненты
│   └── layout/            # Layout компоненты
│       ├── Layout.jsx     # Основной layout с Outlet
│       ├── Header.jsx     # Шапка с навигацией
│       └── Footer.jsx     # Подвал
├── pages/                 # Страницы приложения
│   ├── Home.jsx           # Главная страница
│   ├── Catalog.jsx        # Каталог с фильтрами
│   ├── Product.jsx        # Страница товара
│   └── Cart.jsx           # Корзина
├── store/                 # Zustand stores
│   └── cartStore.js       # Состояние корзины
├── hooks/                 # Custom hooks
├── utils/                 # Утилиты
└── styles/                # Глобальные стили

```

## Основные возможности

### API Integration

Все API endpoints из backend интегрированы:

- **Категории**: получение дерева категорий, информации, фильтров, фасетов
- **Продукты**: список с фильтрацией, детали товара, SKU, похожие товары
- **Корзина**: добавление/удаление/обновление товаров, управление сессией

### Управление состоянием

**Cart Store** (Zustand):
- `fetchCart()` - загрузка корзины
- `addItem(skuId, quantity)` - добавление товара
- `updateItem(itemId, quantity)` - обновление количества
- `removeItem(itemId)` - удаление товара
- `clearCart()` - очистка корзины
- `getItemCount()` - количество товаров
- `getTotalPrice()` - общая сумма

### Роутинг

- `/` - Главная страница
- `/catalog?category=<id>` - Каталог товаров
- `/product/:id` - Страница товара
- `/cart` - Корзина

## Запуск проекта

### Установка зависимостей

```bash
npm install
```

### Настройка окружения

Создайте файл `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Запуск dev сервера

```bash
npm run dev
```

Приложение будет доступно на http://localhost:5173/

### Сборка для production

```bash
npm run build
```

### Preview production сборки

```bash
npm run preview
```

## API Client

API клиент автоматически:
- Добавляет `X-Session-Id` или `X-User-Id` заголовки
- Генерирует session ID при первом запросе
- Обрабатывает ошибки
- Сохраняет сессию в localStorage

## Расширение функционала

### Добавление новой страницы

1. Создайте компонент в `src/pages/`
2. Добавьте роут в `src/App.jsx`
3. Добавьте ссылку в навигацию (`Header.jsx`)

### Добавление нового API endpoint

1. Добавьте метод в соответствующий файл в `src/api/`
2. Используйте в компонентах или создайте store

### Создание нового store

```javascript
import { create } from 'zustand';

const useMyStore = create((set) => ({
  data: null,
  loading: false,
  
  fetchData: async () => {
    set({ loading: true });
    // fetch logic
    set({ data: result, loading: false });
  },
}));

export default useMyStore;
```

## Следующие шаги

- [ ] Добавить поиск товаров
- [ ] Реализовать фильтрацию в каталоге
- [ ] Добавить пагинацию
- [ ] Улучшить UI/UX (добавить loading states, skeleton screens)
- [ ] Добавить обработку ошибок с уведомлениями
- [ ] Реализовать авторизацию
- [ ] Добавить breadcrumbs навигацию
- [ ] Оптимизировать изображения товаров
- [ ] Добавить адаптивную верстку для мобильных устройств
- [ ] Написать тесты

## Backend

Backend API находится в `services/b2c` и должен быть запущен на порту 8000.
