from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, Coords, Level, Pereval, Image
import json


class PerevalModelTest(TestCase):
    """Тесты для моделей базы данных"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create(
            email='test@example.com',
            last_name='Иванов',
            first_name='Иван',
            middle_name='Иванович',
            phone='+79991234567'
        )

        self.coords = Coords.objects.create(
            latitude=45.123456,
            longitude=38.123456,
            height=1500
        )

        self.level = Level.objects.create(
            winter='1A',
            summer='1B',
            autumn='2A',
            spring='1B'
        )

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.last_name, 'Иванов')
        self.assertEqual(self.user.get_full_name(), 'Иванов Иван Иванович')

    def test_coords_creation(self):
        """Тест создания координат"""
        self.assertEqual(self.coords.latitude, 45.123456)
        self.assertEqual(self.coords.longitude, 38.123456)
        self.assertEqual(self.coords.height, 1500)
        self.assertTrue(self.coords.is_high_mountain(1000))  # Выше 1000м - высокогорье

    def test_level_creation(self):
        """Тест создания уровня сложности"""
        self.assertEqual(self.level.winter, '1A')
        self.assertEqual(self.level.summer, '1B')

    def test_pereval_creation(self):
        """Тест создания перевала"""
        pereval = Pereval.objects.create(
            beauty_title='пер. ',
            title='Пereвал',
            other_titles='Другие названия',
            connect='Хорошее соединение',
            user=self.user,
            coords=self.coords,
            level=self.level
        )

        self.assertEqual(pereval.title, 'Пereвал')
        self.assertEqual(pereval.status, 'new')
        self.assertEqual(str(pereval), 'Пereвал')

    def test_image_creation(self):
        """Тест создания изображения"""
        pereval = Pereval.objects.create(
            title='Тестовый перевал',
            user=self.user,
            coords=self.coords,
            level=self.level
        )

        image = Image.objects.create(
            pereval=pereval,
            file_path='/path/to/image.jpg',
            title='Красивый вид'
        )

        self.assertEqual(image.title, 'Красивый вид')
        self.assertEqual(str(image), 'Красивый вид')


class PerevalAPITest(TestCase):
    """Тесты для REST API"""

    def setUp(self):
        """Настройка клиента и тестовых данных"""
        self.client = APIClient()

        # Тестовые данные для отправки
        self.valid_pereval_data = {
            "beauty_title": "пер. ",
            "title": "Пereвал",
            "other_titles": "Другое название",
            "connect": "Хорошее соединение",
            "user": {
                "email": "test@example.com",
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
                },
                {
                    "file_path": "/path/to/image2.jpg",
                    "title": "Подъём"
                }
            ]
        }

    def test_submit_data_create_pereval(self):
        """Тест создания перевала через POST /submitData/"""
        response = self.client.post(
            reverse('submit-data'),
            data=json.dumps(self.valid_pereval_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], status.HTTP_200_OK)
        self.assertIsNotNone(response.data['id'])

        # Проверяем, что перевал создан в базе данных
        pereval_id = response.data['id']
        pereval = Pereval.objects.get(id=pereval_id)
        self.assertEqual(pereval.title, 'Пereвал')
        self.assertEqual(pereval.user.email, 'test@example.com')

    def test_get_pereval_by_id(self):
        """Тест получения перевала по ID через GET /submitData/<id>/"""
        # Сначала создаем перевал
        response = self.client.post(
            reverse('submit-data'),
            data=json.dumps(self.valid_pereval_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pereval_id = response.data['id']

        # Затем получаем его по ID
        response = self.client.get(reverse('submit-data-detail', kwargs={'pk': pereval_id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Пereвал')
        self.assertEqual(response.data['coords']['latitude'], 45.123456)
        self.assertEqual(len(response.data['images']), 2)

    def test_update_pereval_success(self):
        """Тест успешного обновления перевала через PATCH /submitData/<id>/update/"""
        # Создаем перевал
        response = self.client.post(
            reverse('submit-data'),
            data=json.dumps(self.valid_pereval_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pereval_id = response.data['id']

        # Обновляем перевал (статус 'new' по умолчанию)
        update_data = {
            "beauty_title": "пер. Обновленный",
            "title": "Обновленный перевал",
            "other_titles": "Новое другое название",
            "connect": "Обновленное соединение",
            "coords": {
                "latitude": 46.123456,
                "longitude": 39.123456,
                "height": 1600
            },
            "level": {
                "winter": "2A",
                "summer": "2B"
            },
            "images": [
                {
                    "file_path": "/path/to/new_image.jpg",
                    "title": "Новый вид"
                }
            ]
        }

        response = self.client.patch(
            reverse('submit-data-update', kwargs={'pk': pereval_id}),
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 1)
        self.assertIn('успешно', response.data['message'])

        # Проверяем, что данные обновились
        updated_pereval = Pereval.objects.get(id=pereval_id)
        self.assertEqual(updated_pereval.title, 'Обновленный перевал')
        self.assertEqual(updated_pereval.coords.latitude, 46.123456)

    def test_update_pereval_not_allowed_status(self):
        """Тест попытки обновления перевала с недопустимым статусом"""
        # Создаем перевал
        response = self.client.post(
            reverse('submit-data'),
            data=json.dumps(self.valid_pereval_data),
            content_type='application/json'
        )

        pereval_id = response.data['id']

        # Меняем статус на 'pending'
        pereval = Pereval.objects.get(id=pereval_id)
        pereval.status = 'pending'
        pereval.save()

        # Пытаемся обновить
        update_data = {"title": "Новый заголовок"}
        response = self.client.patch(
            reverse('submit-data-update', kwargs={'pk': pereval_id}),
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['state'], 0)

    def test_get_user_perevals(self):
        """Тест получения списка перевалов пользователя через GET /submitData/?user__email="""
        # Создаем несколько перевалов для одного пользователя
        for i in range(2):
            pereval_data = self.valid_pereval_data.copy()
            pereval_data['title'] = f'Перевал {i + 1}'
            pereval_data['coords']['latitude'] = 45.0 + i
            pereval_data['coords']['longitude'] = 38.0 + i

            response = self.client.post(
                reverse('submit-data'),
                data=json.dumps(pereval_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Получаем список перевалов пользователя
        response = self.client.get(
            reverse('submit-data-user-list'),
            {'user__email': 'test@example.com'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['user']['email'], 'test@example.com')

    def test_get_user_perevals_user_not_found(self):
        """Тест получения перевалов несуществующего пользователя"""
        response = self.client.get(
            reverse('submit-data-user-list'),
            {'user__email': 'nonexistent@example.com'}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_pereval_data(self):
        """Тест отправки невалидных данных"""
        invalid_data = self.valid_pereval_data.copy()
        invalid_data['coords']['latitude'] = 100  # Недопустимое значение широты

        response = self.client.post(
            reverse('submit-data'),
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], status.HTTP_400_BAD_REQUEST)

    def test_integration_workflow(self):
        """Интеграционный тест: создание -> получение -> обновление -> получение обновленных данных"""
        # 1. Создаем перевал
        response = self.client.post(
            reverse('submit-data'),
            data=json.dumps(self.valid_pereval_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pereval_id = response.data['id']

        # 2. Получаем созданный перевал
        response = self.client.get(reverse('submit-data-detail', kwargs={'pk': pereval_id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Пereвал')
        self.assertEqual(response.data['user']['email'], 'test@example.com')

        # 3. Обновляем перевал
        update_data = {
            "beauty_title": "пер. Интеграционный",
            "title": "Интеграционный перевал",
            "coords": {
                "latitude": 47.0,
                "longitude": 40.0,
                "height": 2000
            }
        }

        response = self.client.patch(
            reverse('submit-data-update', kwargs={'pk': pereval_id}),
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 1)

        # 4. Получаем обновленный перевал
        response = self.client.get(reverse('submit-data-detail', kwargs={'pk': pereval_id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Интеграционный перевал')
        self.assertEqual(response.data['coords']['latitude'], 47.0)
        self.assertEqual(response.data['coords']['height'], 2000)

        # 5. Проверяем, что пользовательские данные не изменились
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertEqual(response.data['user']['last_name'], 'Иванов')


class PerevalEdgeCasesTest(TestCase):
    """Тесты для граничных случаев"""

    def setUp(self):
        self.client = APIClient()

        self.minimal_pereval_data = {
            "title": "Минимальный перевал",
            "user": {
                "email": "minimal@example.com",
                "last_name": "Минимал",
                "first_name": "Мин",
                "phone": "+79990000000"
            },
            "coords": {
                "latitude": -90.0,  # Минимальная широта
                "longitude": -180.0,  # Минимальная долгота
                "height": 0
            },
            "level": {
                "winter": "4A",
                "summer": "4B"
            },
            "images": []
        }

    def test_min_max_coordinates(self):
        """Тест минимальных и максимальных значений координат"""
        # Тест минимальных значений
        response = self.client.post(
            reverse('submit-data'),
            data=json.dumps(self.minimal_pereval_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Тест максимальных значений
        max_coords_data = self.minimal_pereval_data.copy()
        max_coords_data['coords'] = {
            "latitude": 90.0,  # Максимальная широта
            "longitude": 180.0,  # Максимальная долгота
            "height": 9999
        }
        max_coords_data['user']['email'] = 'max@example.com'
        max_coords_data['title'] = 'Максимальные координаты'

        response = self.client.post(
            reverse('submit-data'),
            data=json.dumps(max_coords_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_optional_fields(self):
        """Тест пустых необязательных полей"""
        data_with_empty_fields = self.minimal_pereval_data.copy()
        data_with_empty_fields['beauty_title'] = ''
        data_with_empty_fields['other_titles'] = ''
        data_with_empty_fields['connect'] = ''
        data_with_empty_fields['user']['middle_name'] = ''
        data_with_empty_fields['user']['email'] = 'empty@example.com'
        data_with_empty_fields['title'] = 'Перевал с пустыми полями'

        response = self.client.post(
            reverse('submit-data'),
            data=json.dumps(data_with_empty_fields),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)