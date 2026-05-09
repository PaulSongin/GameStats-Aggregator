# GameStats Aggregator - PostgreSQL Setup

## Что было добавлено

### 1. PostgreSQL в Docker Compose
- Контейнер PostgreSQL 16 Alpine
- База данных: `gamestats`
- Credentials: `admin` / `admin123`
- Порт: `5432`
- Persistent volume для данных

### 2. Entity Framework Core
Установлены пакеты:
- `Microsoft.EntityFrameworkCore` 10.0.0
- `Microsoft.EntityFrameworkCore.Design` 10.0.0
- `Npgsql.EntityFrameworkCore.PostgreSQL` 10.0.0

### 3. Модели данных
- `UserProfile` - профили пользователей по платформам
- `GameRecord` - записи об играх с временем игры
- `AppDbContext` - контекст базы данных

### 4. Функциональность кэширования
StatsController теперь:
- Проверяет кэш в БД (30 минут)
- Сохраняет данные после запроса к API
- Поддерживает принудительное обновление через `?refresh=true`

## Как использовать

### Запуск проекта
```bash
docker-compose up --build
```

### API эндпоинты
```
# Получить данные (с кэшем)
GET http://localhost:5000/api/stats/steam/76561198012345678

# Принудительно обновить данные
GET http://localhost:5000/api/stats/steam/76561198012345678?refresh=true
```

### Подключение к PostgreSQL
```bash
# Из хоста
psql -h localhost -p 5432 -U admin -d gamestats

# Пароль: admin123
```

### Управление миграциями
```bash
cd CoreBackend

# Создать новую миграцию
dotnet ef migrations add MigrationName

# Применить миграции
dotnet ef database update

# Откатить миграцию
dotnet ef migrations remove
```

## Структура БД

### Таблица UserProfiles
- Id (PK)
- Platform (steam/psn/xbox)
- UserId (внешний ID пользователя)
- LastUpdated (время последнего обновления)
- Unique Index: (Platform, UserId)

### Таблица GameRecords
- Id (PK)
- ExternalId (ID игры на платформе)
- Title (название игры)
- PlaytimeMinutes (время игры в минутах)
- IconUrl (ссылка на иконку)
- UserProfileId (FK)

## Безопасность

⚠️ **Для продакшена:**
1. Измените пароли в `docker-compose.yml`
2. Используйте переменные окружения для credentials
3. Добавьте `.env` файл в `.gitignore`
