from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Car Store API",
      default_version='v1',
      description="API documentation for the Car Store project",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="support@carstore.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('accounts/api/v1', include('accounts.api.v1.urls')),
    path('products/api/v1', include('products.api.v1.urls')),
    path('ads/api/v1', include('ads.api.v1.urls')),
    path('payment/api/v1', include('payment.api.v1.urls')),
]
