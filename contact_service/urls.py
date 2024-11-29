"""contact_service URL Configuration
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.conf import settings
from django.conf.urls.static import static

from contact_service.router_urls import router_urlpatterns

from common.choices import EnvironmentChoices
from contact.api.viewsets import UpdatePhoneNumberView

def trigger_error(request):
    raise ValueError("[SENTRY] -- This is a deliberate error for testing purposes")

urlpatterns = [
    path("api/contacts/admin/", admin.site.urls),
    path("api/", include(router_urlpatterns)),
    path("api-auth/", include("rest_framework.urls")),
    path("api/contacts/sentry-debug/", trigger_error),
    path('user/update_phone/', UpdatePhoneNumberView.as_view(), name='update-phone'),
]


# Restrict access to schema according to Environment
if settings.ENVIRONMENT not in [
    EnvironmentChoices.PRODUCTION.value,
    EnvironmentChoices.QA.value,
]:
    urlpatterns += [
        path("api/contacts/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/contacts/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/contacts/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
        path('api/contacts/user/update_phone/',
        UpdatePhoneNumberView.as_view(),
        name='update-phone'
        ),
    ]



urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

