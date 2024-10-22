from rest_framework import routers
from django.urls import path

from contact.api.viewsets import ContactViewSet, ExternalRequestView

router = routers.DefaultRouter()
router.register(r"contacts", ContactViewSet, basename="contacts")


urlpatterns = [
    path("external_request/", ExternalRequestView.as_view(), name="external_request"),
]
