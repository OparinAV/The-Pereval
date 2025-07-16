
**REST API для учёта данных о горных перевалах**  
Проект позволяет туристам добавлять информацию о перевалах и просматривать существующие записи.

**Пример запроса:**
```json
{
    "beauty_title": "пер. ",
    "title": "Пхия",
    "other_titles": "Триев",
    "connect": "",
    "add_time": "2025-07-01 21:00",
    "user": {
        "email": "test@yandex.ru",
        "last_name": "Иванов",
        "first_name": "Иван",
        "middle_name": "Иванович",
        "phone": "3-22-2-33-322"
    },
    "coords": {
        "latitude": "45.3842",
        "longitude": "7.1525",
        "height": "1200"
    },
    "level": {
        "winter": "",
        "summer": "1А",
        "autumn": "1А",
        "spring": ""
    },
    "images": [
        {"file_path": "седловина.jpg", "title": "Седловина"},
        {"file_path": "подъем.jpg", "title": "Подъём"}
    ]
}
Ответ:

json
{
  "status": 200,
  "message": null,
  "id": 42
}

2. Просмотр перевала (GET /submitData/42/)
Ответ:

json
{
  "id": 42,
  "status": "new",
  "title": "Пхия",
  "user": {
    "email": "test@yandex.ru",
    "phone": "3-22-2-33-322",
    "last_name": "Иванов"
  },
  "coords": {
    "latitude": 45.3842,
    "longitude": 7.1525
  },
  "images": []
}

Возможные ответы:

Статус	Тело ответа
201	{"status": 201, "id": 123}
400	{"error": "Invalid email format"}
500	{"error": "Database error"}
