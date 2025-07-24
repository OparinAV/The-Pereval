from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Pereval, User, Coords, Level, Image
from .serializers import PerevalSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction


class SubmitDataView(APIView):
    def post(self, request):
        serializer = PerevalSerializer(data=request.data)

        if serializer.is_valid():
            try:
                pereval = serializer.save()
                response_data = {
                    'status': status.HTTP_200_OK,
                    'message': None,
                    'id': pereval.id
                }
                return Response(response_data, status=status.HTTP_200_OK)
            except Exception as e:
                response_data = {
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'message': f"Ошибка при сохранении данных: {str(e)}",
                    'id': None
                }
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            errors = serializer.errors
            error_messages = []

            for field, messages in errors.items():
                for message in messages:
                    error_messages.append(f"{field}: {message}")

            response_data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': "; ".join(error_messages),
                'id': None
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class PerevalDetailView(RetrieveAPIView):
    queryset = Pereval.objects.all()
    serializer_class = PerevalSerializer



class SubmitDataDetail(APIView):
    """
    GET /submitData/<id> — получить одну запись (перевал) по её id
    """

    @swagger_auto_schema(
        operation_description="Получить информацию о перевале по ID",
        responses={200: PerevalSerializer}
    )
    def get(self, request, pk):
        pereval = get_object_or_404(Pereval, pk=pk)
        serializer = PerevalSerializer(pereval)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmitDataUpdate(APIView):
    """
    PATCH /submitData/<id> — отредактировать существующую запись, если она в статусе new
    """

    @swagger_auto_schema(
        operation_description="Редактировать перевал (только если статус 'new')",
        request_body=PerevalSerializer,
        responses={
            200: openapi.Response(
                description="Результат обновления",
                examples={
                    "application/json": {
                        "state": 1,
                        "message": "Запись успешно обновлена"
                    }
                }
            )
        }
    )
    def patch(self, request, pk):
        try:
            pereval = get_object_or_404(Pereval, pk=pk)

            # Проверяем, что запись в статусе 'new'
            if pereval.status != 'new':
                return Response({
                    'state': 0,
                    'message': f'Запись не может быть отредактирована, так как её статус: {pereval.get_status_display_rus()}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Получаем данные из запроса
            data = request.data.copy()

            # Удаляем поля пользователя, которые нельзя редактировать
            user_data = data.pop('user', None)

            # Обновляем основные данные перевала
            updatable_fields = ['beauty_title', 'title', 'other_titles', 'connect']
            for field in updatable_fields:
                if field in data:
                    setattr(pereval, field, data[field])

            # Обновляем координаты
            if 'coords' in data:
                coords_data = data['coords']
                if pereval.coords:
                    # Обновляем существующие координаты
                    for field, value in coords_data.items():
                        setattr(pereval.coords, field, value)
                    pereval.coords.save()
                else:
                    # Создаем новые координаты
                    coords = Coords.objects.create(**coords_data)
                    pereval.coords = coords

            # Обновляем уровень сложности
            if 'level' in data:
                level_data = data['level']
                if pereval.level:
                    # Обновляем существующий уровень
                    for field, value in level_data.items():
                        setattr(pereval.level, field, value)
                    pereval.level.save()
                else:
                    # Создаем новый уровень
                    level = Level.objects.create(**level_data)
                    pereval.level = level

            # Сохраняем изменения в основном объекте
            pereval.save()

            # Обновляем изображения, если они переданы
            if 'images' in data:
                # Удаляем старые изображения
                pereval.images.all().delete()
                # Создаем новые изображения
                for img_data in data['images']:
                    Image.objects.create(
                        pereval=pereval,
                        file_path=img_data.get('file_path', ''),
                        title=img_data.get('title', '')
                    )

            return Response({
                'state': 1,
                'message': 'Запись успешно обновлена'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'state': 0,
                'message': f'Ошибка при обновлении записи: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class SubmitDataUserList(APIView):
    """
    GET /submitData/?user__email=<email> — список данных обо всех объектах пользователя
    """

    @swagger_auto_schema(
        operation_description="Получить список перевалов пользователя по email",
        manual_parameters=[
            openapi.Parameter(
                'user__email',
                openapi.IN_QUERY,
                description="Email пользователя",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: PerevalSerializer(many=True)}
    )
    def get(self, request):
        email = request.query_params.get('user__email')

        if not email:
            return Response({
                'error': 'Параметр user__email обязателен'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            perevals = Pereval.objects.filter(user=user)
            serializer = PerevalSerializer(perevals, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'error': 'Пользователь с таким email не найден'
            }, status=status.HTTP_404_NOT_FOUND)