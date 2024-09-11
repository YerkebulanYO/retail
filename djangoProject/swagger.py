import os
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from django.urls import path

from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="DJANGO RETAIL PROJECT",
        default_version="v1",
        description="Description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="erkebulan122@mail.com"),
        license=openapi.License(name="BSD License"),
    ),
    url=os.getenv("CURRENT_SITE"),
    public=True,
    permission_classes=[permissions.AllowAny],
)

swagger_patterns = [
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
