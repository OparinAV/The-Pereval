from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Pereval
from .serializers import PerevalSerializer
from rest_framework import status


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