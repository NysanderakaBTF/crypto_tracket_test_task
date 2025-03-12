# Crypto Price Tracker

Это Django-приложение для отслеживания цен криптовалют в реальном времени через WebSocket и предоставления исторических данных через REST API. Приложение подключается к публичному WebSocket API Binance для получения данных о ценах, сохраняет их в PostgreSQL и использует Redis как бэкенд для Django Channels.

Требования:
* Docker (для запуска в контейнерах)

## Запуск

Запустите Docker Compose:
``` 
docker-compose up --build 
```

Это создаст и запустит контейнеры для Django, PostgreSQL и Redis.

Остановка:
```
docker-compose down
```

## Использование
### WebSocket

Для получения обновлений цен в реальном времени подключитесь к WebSocket-эндпоинту:
```
ws://localhost:8000/ws/prices/<ticket>
```
Пример:
```
ws://localhost:8000/ws/prices/btcusdt
```

### REST API
Для получения истории цен используйте REST-эндпоинт:
```
http://localhost:8000/prices?ticket=<ticket>
```
Пример:
```
http://localhost:8000/prices?ticket=ethusdt
```

## Тестирование

Для запуска тестов используйте команду
```
docker-compose run web pytest .
```