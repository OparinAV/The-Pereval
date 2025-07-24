from rest_framework import serializers
from .models import User, Coords, Level, Pereval, Image


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'last_name', 'first_name', 'middle_name', 'phone']
        read_only_fields = ['email', 'last_name', 'first_name', 'middle_name', 'phone']


class CoordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coords
        fields = ['latitude', 'longitude', 'height']


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['winter', 'summer', 'autumn', 'spring']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['file_path', 'title']


class PerevalSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    coords = CoordsSerializer()
    level = LevelSerializer()
    images = ImageSerializer(many=True)

    class Meta:
        model = Pereval
        fields = ['id', 'beauty_title', 'title', 'other_titles', 'connect', 'add_time',
                  'status', 'user', 'coords', 'level', 'images']
        read_only_fields = ['id', 'add_time', 'status']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        coords_data = validated_data.pop('coords')
        level_data = validated_data.pop('level')
        images_data = validated_data.pop('images', [])

        # Создаем пользователя или получаем существующего
        user, _ = User.objects.get_or_create(email=user_data['email'], defaults=user_data)

        # Создаем координаты
        coords = Coords.objects.create(**coords_data)

        # Создаем уровень сложности
        level = Level.objects.create(**level_data)

        # Создаем перевал
        pereval = Pereval.objects.create(
            user=user,
            coords=coords,
            level=level,
            **validated_data
        )

        # Создаем изображения
        for image_data in images_data:
            if isinstance(image_data, dict):  # Проверяем, что данные являются словарем
                Image.objects.create(pereval=pereval, **image_data)

        return pereval

    def update(self, instance, validated_data):
        # Извлекаем вложенные данные
        user_data = validated_data.pop('user', None)
        coords_data = validated_data.pop('coords', None)
        level_data = validated_data.pop('level', None)
        images_data = validated_data.pop('images', None)

        # Обновляем основные поля перевала
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Обновляем координаты (если переданы)
        if coords_data and instance.coords:
            for attr, value in coords_data.items():
                setattr(instance.coords, attr, value)
            instance.coords.save()
        elif coords_data:
            # Если координат нет, создаем новые
            coords = Coords.objects.create(**coords_data)
            instance.coords = coords

        # Обновляем уровень сложности (если передан)
        if level_data and instance.level:
            for attr, value in level_data.items():
                setattr(instance.level, attr, value)
            instance.level.save()
        elif level_data:
            # Если уровня нет, создаем новый
            level = Level.objects.create(**level_data)
            instance.level = level

        # Обновляем изображения (если переданы)
        if images_data is not None:
            # Удаляем старые изображения
            instance.images.all().delete()
            # Создаем новые изображения
            for image_data in images_data:
                if isinstance(image_data, dict):  # Проверяем, что данные являются словарем
                    Image.objects.create(pereval=instance, **image_data)

        instance.save()
        return instance