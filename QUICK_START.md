# 🚀 Быстрый запуск проекта

## Скрипты для управления проектом

### Основные команды

#### `start-all.bat` - Запустить весь проект
Запускает Docker контейнеры (бэкенд, БД, Redis) и фронтенд одной командой.
```bash
# Просто дважды кликни на файл или запусти:
start-all.bat
```

#### `start.bat` - Запустить только Docker сервисы
Запускает бэкенд, базу данных и Redis без пересборки.
```bash
start.bat
```

#### `start-frontend.bat` - Запустить только фронтенд
Запускает Next.js dev сервер.
```bash
start-frontend.bat
```

#### `stop.bat` - Остановить Docker сервисы
Останавливает все Docker контейнеры.
```bash
stop.bat
```

#### `stop-all.bat` - Остановить все сервисы
Останавливает Docker контейнеры (фронтенд нужно закрыть вручную через Ctrl+C).
```bash
stop-all.bat
```

#### `rebuild.bat` - Пересобрать и запустить Docker сервисы
Используй только когда изменился код бэкенда или зависимости.
```bash
rebuild.bat
```

---

## Когда использовать какой скрипт?

### Обычный запуск (каждый день)
✅ **Используй:** `start-all.bat`
- Запускает все сервисы без пересборки
- Быстро и просто

### Изменился код бэкенда (.NET или Python)
✅ **Используй:** `rebuild.bat` + `start-frontend.bat`
- Пересобирает Docker образы
- Применяет изменения в коде

### Изменился только фронтенд
✅ **Используй:** просто перезагрузи страницу в браузере
- Next.js автоматически применяет изменения (Hot Reload)

### Остановить проект
✅ **Используй:** `stop-all.bat`
- Останавливает все Docker контейнеры
- Фронтенд закрой вручную (Ctrl+C в терминале)

---

## URL сервисов

После запуска проект доступен по адресам:

- 🌐 **Frontend:** http://localhost:3000
- 🔧 **Backend API:** http://localhost:5000
- 🐍 **Python Provider:** http://localhost:8000
- 🗄️ **PostgreSQL:** localhost:5433
- 🔴 **Redis:** localhost:6379

---

## Автоматический перезапуск

Docker контейнеры настроены на автоматический перезапуск (`restart: always`).
Это означает:
- ✅ Контейнеры запустятся автоматически при старте Docker Desktop
- ✅ Контейнеры перезапустятся автоматически при сбое
- ✅ Не нужно каждый раз запускать вручную

Чтобы включить автозапуск Docker Desktop при старте Windows:
1. Открой Docker Desktop
2. Settings → General
3. Включи "Start Docker Desktop when you log in"

---

## Troubleshooting

### Порты заняты
Если видишь ошибку "port is already allocated":
```bash
# Останови все контейнеры
stop.bat

# Проверь, что порты свободны
netstat -ano | findstr "3000 5000 8000 5433 6379"

# Запусти снова
start-all.bat
```

### Контейнеры не запускаются
```bash
# Полная перезагрузка
stop.bat
rebuild.bat
start-frontend.bat
```

### Фронтенд не подключается к бэкенду
Проверь, что все контейнеры запущены:
```bash
docker ps
```

Должны быть запущены 4 контейнера:
- gamestatsaggregator-core-backend-1
- gamestatsaggregator-python-provider-1
- gamestatsaggregator-postgres-1
- gamestatsaggregator-redis-1
