import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env файла


class PerevalDatabase:
    def __init__(self):
        self.db_host = os.getenv('FSTR_DB_HOST')
        self.db_port = os.getenv('FSTR_DB_PORT')
        self.db_login = os.getenv('FSTR_DB_LOGIN')
        self.db_pass = os.getenv('FSTR_DB_PASS')
        self.db_name = 'pereval'  # Можно также вынести в переменные окружения
        self.conn = None
        self.cursor = None

    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                dbname=self.db_name,
                user=self.db_login,
                password=self.db_pass,
                cursor_factory=DictCursor,
            )
            self.cursor = self.conn.cursor()
            print("Успешное подключение к базе данных")
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise

    def disconnect(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()
            print("Соединение с базой данных закрыто")

    def submit_data(self, pereval_data):
        """
        Добавление нового перевала в базу данных
        :param pereval_data: словарь с данными о перевале
        :return: ID созданной записи или None в случае ошибки
        """
        try:
            self.connect()

            # 1. Сначала добавляем пользователя (если его нет)
            user_id = self._add_user(pereval_data.get('user'))
            if not user_id:
                raise ValueError("Не удалось добавить пользователя")

            # 2. Добавляем координаты
            coords = pereval_data.get('coords')
            coord_id = self._add_coords(
                latitude=coords.get('latitude'),
                longitude=coords.get('longitude'),
                height=coords.get('height')
            )
            if not coord_id:
                raise ValueError("Не удалось добавить координаты")

            # 3. Добавляем уровни сложности
            levels = pereval_data.get('level')
            level_id = self._add_levels(
                winter=levels.get('winter'),
                summer=levels.get('summer'),
                autumn=levels.get('autumn'),
                spring=levels.get('spring')
            )
            if not level_id:
                raise ValueError("Не удалось добавить уровни сложности")

            # 4. Добавляем сам перевал
            pereval_id = self._add_pereval(
                beauty_title=pereval_data.get('beautyTitle'),
                title=pereval_data.get('title'),
                other_titles=pereval_data.get('other_titles'),
                connect=pereval_data.get('connect'),
                add_time=pereval_data.get('add_time'),
                user_id=user_id,
                coord_id=coord_id,
                level_id=level_id,
                area_id=pereval_data.get('area_id'),
                activity_type=pereval_data.get('activity_type')
            )

            # 5. Добавляем изображения
            images = pereval_data.get('images', [])
            for image in images:
                self._add_image(
                    pereval_id=pereval_id,
                    title=image.get('title'),
                    file_path=image.get('file_path'),
                    file_size=image.get('file_size'),
                    file_type=image.get('file_type'),
                    width=image.get('width'),
                    height=image.get('height'),
                    uploaded_by=user_id
                )

            self.conn.commit()
            return pereval_id

        except Exception as e:
            print(f"Ошибка при добавлении перевала: {e}")
            if self.conn:
                self.conn.rollback()
            return None
        finally:
            self.disconnect()

    def _add_user(self, user_data):
        """Добавление пользователя в базу данных"""
        query = sql.SQL("""
            INSERT INTO users (email, phone, last_name, first_name, middle_name)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET
                phone = EXCLUDED.phone,
                last_name = EXCLUDED.last_name,
                first_name = EXCLUDED.first_name,
                middle_name = EXCLUDED.middle_name
            RETURNING id
        """)
        try:
            self.cursor.execute(query, (
                user_data.get('email'),
                user_data.get('phone'),
                user_data.get('fam'),
                user_data.get('name'),
                user_data.get('otc')
            ))
            return self.cursor.fetchone()['id']
        except Exception as e:
            print(f"Ошибка при добавлении пользователя: {e}")
            return None

    def _add_coords(self, latitude, longitude, height):
        """Добавление координат"""
        query = sql.SQL("""
            INSERT INTO coords (latitude, longitude, height)
            VALUES (%s, %s, %s)
            RETURNING id
        """)
        try:
            self.cursor.execute(query, (latitude, longitude, height))
            return self.cursor.fetchone()['id']
        except Exception as e:
            print(f"Ошибка при добавлении координат: {e}")
            return None

    def _add_levels(self, winter, summer, autumn, spring):
        """Добавление уровней сложности"""
        query = sql.SQL("""
            INSERT INTO pereval_levels (winter, summer, autumn, spring)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """)
        try:
            self.cursor.execute(query, (winter, summer, autumn, spring))
            return self.cursor.fetchone()['id']
        except Exception as e:
            print(f"Ошибка при добавлении уровней сложности: {e}")
            return None

    def _add_pereval(self, beauty_title, title, other_titles, connect, add_time,
                     user_id, coord_id, level_id, area_id=None, activity_type=None):
        """Добавление информации о перевале"""
        query = sql.SQL("""
            INSERT INTO pereval_added (
                beauty_title, title, other_titles, connect, add_time,
                user_id, coord_id, level_id, area_id, activity_type, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'new')
            RETURNING id
        """)
        try:
            self.cursor.execute(query, (
                beauty_title, title, other_titles, connect, add_time,
                user_id, coord_id, level_id, area_id, activity_type
            ))
            return self.cursor.fetchone()['id']
        except Exception as e:
            print(f"Ошибка при добавлении перевала: {e}")
            return None

    def _add_image(self, pereval_id, title, file_path, file_size=None,
                   file_type=None, width=None, height=None, uploaded_by=None):
        """Добавление изображения"""
        query = sql.SQL("""
            INSERT INTO pereval_images (
                title, file_path, file_size, file_type, width, height, uploaded_by
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """)
        try:
            self.cursor.execute(query, (
                title, file_path, file_size, file_type, width, height, uploaded_by
            ))
            image_id = self.cursor.fetchone()['id']

            # Связываем изображение с перевалом
            link_query = sql.SQL("""
                INSERT INTO pereval_images_links (pereval_id, image_id)
                VALUES (%s, %s)
            """)
            self.cursor.execute(link_query, (pereval_id, image_id))
            return image_id
        except Exception as e:
            print(f"Ошибка при добавлении изображения: {e}")
            return None