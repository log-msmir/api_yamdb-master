from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import TemplateView
from django.conf.urls.static import static

from rest_framework import permissions
from rest_framework.schemas import get_schema_view as rest_schema_view

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(openapi.Info(
    title='YaMDB API',
    default_version='v1',
    description='A simple API for learning DRF',
    terms_of_service='https://www.google/com/politicies/terms/',
    contact=openapi.Contact(email='msmir@inbox.ru'),
    license=openapi.License(name='BSD License'),
),
    public=True,
    permission_classes=(permissions.IsAuthenticatedOrReadOnly,))


urlpatterns = [
    path('api/v1/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('redoc/', TemplateView.as_view(template_name='redoc.html'), name='redoc'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('my-redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('schema/', rest_schema_view(title='Base schema')),
    path('schema1/', schema_view.without_ui())
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
