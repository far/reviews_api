## Установка
```bash
pip install fastapi uvicorn "sqlalchemy[asyncio]" aiosqlite
uvicorn main:app --reload
```
## Примеры cURL запросов

### Выборка отзывов с определенным sentiment [positive|negative|neutral]
```console

curl -GET http://127.0.0.1:8000/reviews/\?sentiment\=positive

[{"id":1,"text":"Хорошее приложение","sentiment":"positive","created_at":"2025-07-26T09:06:27.551916"},{"id":2,"text":"Люблю ваше Приложение","sentiment":"positive","created_at":"2025-07-26T09:06:27.551916"}]
```

### Добавление отзыва

```console
curl -H "Content-Type: application/json" -H "Accept: application/json"  -POST -d '{"text":"Хорошее приложение"}' http://127.0.0.1:8000/reviews/

{"id":1,"text":"Хорошее приложение","sentiment":"positive","created_at":"2025-07-26T09:06:27.551916"}
```