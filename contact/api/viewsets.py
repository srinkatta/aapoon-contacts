from rest_framework import permissions, viewsets
from rest_framework.response import Response


from contact.models import Contact
from contact.api.serializers import ContactSerializer
from contact.helpers.mixins import BulkCreateContactMixin
from contact.services.db import Contacts


class ContactViewSet(BulkCreateContactMixin, viewsets.ModelViewSet):
    """
    Viewset for Contact Model
    """

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (permissions.AllowAny,)

    def list(self, request):
        contacts = Contacts().list_contacts()
        return Response(contacts)
