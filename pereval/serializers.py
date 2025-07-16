from rest_framework import serializers
from .models import User, Coords, Level, Pereval, Image


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'last_name', 'first_name', 'middle_name', 'phone']


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
        fields = ['beauty_title', 'title', 'other_titles', 'connect', 'add_time',
                  'user', 'coords', 'level', 'images']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        coords_data = validated_data.pop('coords')
        level_data = validated_data.pop('level')
        images_data = validated_data.pop('images')

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
            Image.objects.create(pereval=pereval, **image_data)

        return pereval