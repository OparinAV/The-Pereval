The_Pereval
REST API для управления данными о горных перевалах. Проект позволяет добавлять, просматривать и редактировать информацию о горных перевалах с привязкой к координатам, сложности и изображениям.

🚀 Основные возможности
Добавление перевалов с полной информацией
Просмотр данных о конкретном перевале
Редактирование перевалов (в статусе "новый")
Фильтрация по пользователю
Swagger документация API
📚 Документация API
Swagger UI : /swagger/
ReDoc : /redoc/
🛠️ Основные эндпоинты
1. Создание перевала
POST /submitData/

Создает новую запись о перевале.

Пример запроса:

```json
{
  "beauty_title": "пер. ",
  "title": "Пereвал",
  "other_titles": "Другое название",
  "connect": "Хорошее соединение",
  "user": {
    "email": "user@example.com",
    "last_name": "Иванов",
    "first_name": "Иван",
    "middle_name": "Иванович",
    "phone": "+79991234567"
  },
  "coords": {
    "latitude": 45.123456,
    "longitude": 38.123456,
    "height": 1500
  },
  "level": {
    "winter": "1A",
    "summer": "1B",
    "autumn": "2A",
    "spring": "1B"
  },
  "images": [
    {
      "file_path": "/path/to/image1.jpg",
      "title": "Седловина"
    }
  ]
}
```
Пример ответа:

```json
{
  "status": 200,
  "message": null,
  "id": 1
}
```
2. Получение перевала по ID
GET /submitData/{id}/

Получает информацию о перевале по его ID.

Пример ответа:

```json
{
  "id": 1,
  "beauty_title": "пер. ",
  "title": "Пereвал",
  "other_titles": "Другое название",
  "connect": "Хорошее соединение",
  "add_time": "2023-12-01T10:30:00Z",
  "status": "new",
  "user": {
    "email": "user@example.com",
    "last_name": "Иванов",
    "first_name": "Иван",
    "middle_name": "Иванович",
    "phone": "+79991234567"
  },
  "coords": {
    "latitude": 45.123456,
    "longitude": 38.123456,
    "height": 1500
  },
  "level": {
    "winter": "1A",
    "summer": "1B",
    "autumn": "2A",
    "spring": "1B"
  },
  "images": [
    {
      "file_path": "/path/to/image1.jpg",
      "title": "Седловина"
    }
  ]
}
```
3. Обновление перевала
PATCH /submitData/{id}/update/

Обновляет существующую запись перевала (только если статус 'new').

⚠️ Важно : Нельзя редактировать данные пользователя (email, ФИО, телефон)

Пример запроса:

```json
{
  "beauty_title": "пер. Обновленный",
  "title": "Обновленный перевал",
  "coords": {
    "latitude": 46.123456,
    "longitude": 39.123456,
    "height": 1600
  },
  "level": {
    "winter": "2A",
    "summer": "2B"
  }
}
```
Пример успешного ответа:

```json
{
  "state": 1,
  "message": "Запись успешно обновлена"
}
```
Пример ошибки:

```json
{
  "state": 0,
  "message": "Запись не может быть отредактирована, так как её статус: модератор взял в работу"
}
```
4. Получение списка перевалов пользователя
GET /submitData/user/?user__email={email}

Получает список всех перевалов пользователя по email.

Пример запроса:

```bash

GET /submitData/user/?user__email=user@example.com
```
Пример ответа:

```json
[
  {
    "id": 1,
    "beauty_title": "пер. ",
    "title": "Пereвал",
    "other_titles": "Другое название",
    "connect": "Хорошее соединение",
    "add_time": "2023-12-01T10:30:00Z",
    "status": "new",
    "user": {
      "email": "user@example.com",
      "last_name": "Иванов",
      "first_name": "Иван",
      "middle_name": "Иванович",
      "phone": "+79991234567"
    },
    "coords": {
      "latitude": 45.123456,
      "longitude": 38.123456,
      "height": 1500
    },
    "level": {
      "winter": "1A",
      "summer": "1B",
      "autumn": "2A",
      "spring": "1B"
    },
    "images": []
  }
]
```
📊 Статусы перевалов 

new - новый (можно редактировать)

pending - модератор взял в работу

accepted - модерация прошла успешно

rejected - модерация прошла, информация не принята

🏗️ Технический стек

Python 3.10+

Django 4.2

Django REST Framework

SQLite/PostgreSQL (в зависимости от среды)

drf-yasg для Swagger документации

drf-spectacular для OpenAPI 3.0

📦 Установка и запуск локально
1. Клонирование репозитория
```bash

git clone https://github.com/OparinAV/The-Pereval.git
cd The_Pereval
```
2. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```
3. Установка зависимостей

pip install -r requirements.txt
4. Настройка базы данных

python manage.py migrate
5. Создание суперпользователя (опционально)

python manage.py createsuperuser

6. Запуск сервера

python manage.py runserver

7. Доступ к приложению

API : http://localhost:8000/

Swagger документация : http://localhost:8000/submitData/swagger/

ReDoc документация : http://localhost:8000/submitData/redoc/

Админ панель : http://localhost:8000/admin/

🧪 Тестирование

Запуск тестов

python manage.py test
