from rest_framework import routers

from contact.api.viewsets import ContactViewSet

router = routers.DefaultRouter()
router.register(r"contacts", ContactViewSet, basename="contacts")
