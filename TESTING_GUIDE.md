# 🎮 Как протестировать GameStats Aggregator

## ✅ Проект запущен и работает!

### 📍 Доступные ссылки:

#### 1. **Core Backend API** (главный API)
```
http://localhost:5000/api/stats/{platform}/{user_id}
```

#### 2. **Cache Metrics** (статистика кэширования)
```
http://localhost:5000/api/stats/metrics
```

#### 3. **Python Provider** (внутренний сервис)
```
http://localhost:8000/
```

#### 4. **Redis Cache**
```
Host: localhost
Port: 6379
```

#### 5. **PostgreSQL Database**
```
Host: localhost
Port: 5433
Database: gamestats
User: admin
Password: admin123
```

---

## 🧪 Примеры запросов

### Steam
Откройте в браузере или используйте curl:
```
http://localhost:5000/api/stats/steam/76561198012345678
```

С принудительным обновлением:
```
http://localhost:5000/api/stats/steam/76561198012345678?refresh=true
```

### PlayStation Network
```
http://localhost:5000/api/stats/psn/YOUR_PSN_ID
```

### Xbox Live
```
http://localhost:5000/api/stats/xbox/YOUR_GAMERTAG
```

---

## 🔍 Как проверить что работает

### 1. Проверить статус контейнеров
```bash
cd "D:\Projects\GameStats Aggregator"
docker-compose ps
```

Все 3 контейнера должны быть в статусе **Up**.

### 2. Проверить Python Provider
Откройте в браузере:
```
http://localhost:8000/
```
Должно вернуть: `{"message":"Data Provider is running"}`

### 3. Проверить Core Backend
Откройте в браузере:
```
http://localhost:5000/api/stats/steam/76561198012345678
```
Должно вернуть JSON с данными игр.

### 4. Проверить базу данных
```bash
docker exec gamestatsaggregator-postgres-1 psql -U admin -d gamestats -c "SELECT * FROM \"UserProfiles\";"
```

---

## 📊 Просмотр данных в PostgreSQL

### Через командную строку:
```bash
# Подключиться к PostgreSQL
docker exec -it gamestatsaggregator-postgres-1 psql -U admin -d gamestats

# Внутри psql:
\dt                                    # Список таблиц
SELECT * FROM "UserProfiles";         # Все профили
SELECT * FROM "GameRecords";          # Все игры
\q                                     # Выход
```

### Через GUI (опционально):
Можете использовать **pgAdmin** или **DBeaver**:
- Host: `localhost`
- Port: `5432`
- Database: `gamestats`
- Username: `admin`
- Password: `admin123`

---

## 🔄 Как работает кэширование

### Двухуровневая система:

1. **Redis (горячий кэш, TTL: 5 минут)**
   - Первая линия защиты
   - Скорость: ~0.5-1 мс
   - Автоматическое истечение

2. **PostgreSQL (холодный кэш, TTL: 30 минут)**
   - Долгосрочное хранилище
   - Скорость: ~10-50 мс
   - История запросов

3. **API (внешние сервисы)**
   - Steam/PSN/Xbox API
   - Скорость: ~500-2000 мс
   - Только при отсутствии в кэше

### Логика запроса:
```
Запрос → Redis → PostgreSQL → API
         ↓ 1ms    ↓ 10ms       ↓ 500ms
```

### Проверить метрики кэширования:
```
http://localhost:5000/api/stats/metrics
```

Пример ответа:
```json
{
  "redisHits": 45,
  "postgresHits": 12,
  "apiCalls": 3,
  "totalRequests": 60,
  "redisHitRate": 75.0,
  "postgresHitRate": 20.0,
  "apiCallRate": 5.0
}
```

---

## 📝 Логи контейнеров

### Посмотреть логи всех сервисов:
```bash
docker-compose logs -f
```

### Логи конкретного сервиса:
```bash
docker-compose logs -f core-backend
docker-compose logs -f python-provider
docker-compose logs -f postgres
```

---

## 🛑 Остановка проекта

```bash
cd "D:\Projects\GameStats Aggregator"
docker-compose down
```

Для удаления данных из БД:
```bash
docker-compose down -v
```

---

## 🚀 Перезапуск после изменений

```bash
docker-compose down
docker-compose up --build -d
```

---

## 🎯 Что дальше?

### Следующие шаги для улучшения проекта:

1. **Добавить Redis** для более быстрого кэширования
2. **Создать фронтенд** (React/Next.js) для красивого отображения
3. **Добавить аутентификацию** пользователей
4. **Вынести API ключи** в переменные окружения (.env файл)
5. **Добавить сравнение достижений** между платформами
6. **Настроить CI/CD** для автоматического деплоя

---

## ⚠️ Важно для продакшена

Перед деплоем на сервер:
- Измените пароли в `docker-compose.yml`
- Вынесите API ключи из `PythonProvider/main.py` в переменные окружения
- Добавьте HTTPS
- Настройте backup базы данных
