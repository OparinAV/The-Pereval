import time
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Pereval, User, Coords, Level, Image


class PerevalAPITests(APITestCase):
    def setUp(self):
        self.submit_url = reverse('submit-data')
        self.valid_data = {
            "beauty_title": "пер. ",
            "title": "Тестовый перевал",
            "other_titles": "Тест-Перевал",
            "connect": "тестовое соединение",
            "add_time": time.strftime("%Y-%m-%d %H:%M:%S"),  # Изменён формат даты
            "user": {
                "email": f"test_{int(time.time())}@example.com",
                "last_name": "Тестов",
                "first_name": "Тест",
                "middle_name": "Тестович",
                "phone": "+7 000 000 00 00"
            },
            "coords": {
                "latitude": "45.0000",
                "longitude": "90.0000",
                "height": "2500"
            },
            "level": {
                "winter": "",
                "summer": "1А",
                "autumn": "1А",
                "spring": ""
            },
            "images": [
                {"file_path": "test_image1.jpg", "title": "Тест фото 1"},
                {"file_path": "test_image2.jpg", "title": "Тест фото 2"}
            ]
        }

    def test_valid_submission(self):
        """Тест успешного создания перевала"""
        response = self.client.post(self.submit_url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Ожидаем 200, а не 201
        self.assertIsNotNone(response.data['id'])

        # Проверка сохранения в БД
        pereval = Pereval.objects.get(id=response.data['id'])
        self.assertEqual(pereval.title, "Тестовый перевал")
        self.assertEqual(pereval.user.first_name, "Тест")
        self.assertEqual(float(pereval.coords.latitude), 45.0000)
        self.assertEqual(pereval.level.summer, "1А")
        self.assertEqual(pereval.images.count(), 2)

    def test_invalid_submission(self):
        """Тест с невалидными данными"""
        invalid_data = {
            "title": "Неполные данные",
            "user": {"email": "invalid@example.com"}
        }

        response = self.client.post(self.submit_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Адаптируем проверку под ваш формат ошибок
        self.assertIn('message', response.data)
        error_message = response.data['message']
        self.assertIn('coords', error_message)
        self.assertIn('level', error_message)
        self.assertIn('images', error_message)

    def test_duplicate_user_email(self):
        """Тест дублирования email пользователя"""
        # Первое успешное создание
        response1 = self.client.post(self.submit_url, self.valid_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Попытка создать с тем же email
        new_data = self.valid_data.copy()
        new_data['title'] = "Новый перевал"
        response2 = self.client.post(self.submit_url, new_data, format='json')

        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response2.data)
        self.assertIn('email', response2.data['message'])

    def test_get_pereval(self):
        """Тест получения данных о перевале"""
        # Сначала создаем
        create_response = self.client.post(self.submit_url, self.valid_data, format='json')
        pereval_id = create_response.data['id']

        # Затем получаем
        detail_url = reverse('pereval-detail', kwargs={'pk': pereval_id})
        get_response = self.client.get(detail_url)

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['title'], "Тестовый перевал")
        self.assertEqual(len(get_response.data['images']), 2)


class ModelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="test@example.com",
            phone="+79991234567",
            last_name="Иванов",
            first_name="Иван",
            middle_name="Иванович"
        )
        self.coords = Coords.objects.create(
            latitude=45.1234,
            longitude=90.5678,
            height=2000
        )
        self.level = Level.objects.create(
            winter="1A",
            summer="1B",
            autumn="",
            spring=""
        )
        self.pereval = Pereval.objects.create(
            beauty_title="пер.",
            title="Тестовый перевал",
            other_titles="Тест",
            connect="",
            user=self.user,
            coords=self.coords,
            level=self.level
        )

    def test_user_str(self):
        """Тест строкового представления пользователя"""
        self.assertEqual(str(self.user), "Иванов Иван Иванович")

    def test_pereval_str(self):
        """Тест строкового представления перевала"""
        self.assertEqual(str(self.pereval), "Тестовый перевал")

    def test_image_relation(self):
        """Тест связи изображения с перевалом"""
        image = Image.objects.create(
            title="Тест фото",
            file_path="test.jpg",
            pereval=self.pereval
        )

        self.assertEqual(image.pereval.title, "Тестовый перевал")
        self.assertEqual(self.pereval.images.count(), 1)
        self.assertEqual(str(image), "Тест фото")