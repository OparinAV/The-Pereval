from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from pereval.views import (
    SubmitDataView,
    PerevalDetailView,
)

# Настройки Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Pereval-Online API",
        default_version='v1',
        description="API для управления данными о горных перевалах",
        terms_of_service="https://your-terms-url.com/",
        contact=openapi.Contact(email="great.egor7288@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Документация
    path('submitData/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('submitData/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('submitData/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API Endpoints
    path('', RedirectView.as_view(url='/submitData/', permanent=False), name='home'),
    path('submitData/', SubmitDataView.as_view(), name='submit-data'),
    path('submitData/<int:pk>/', PerevalDetailView.as_view(), name='pereval-detail'),
]