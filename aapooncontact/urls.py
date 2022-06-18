"""aapooncontact URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

from aapooncontact.router_urls import router_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router_urlpatterns)),
    path("api-auth/", include("rest_framework.urls")),
]
