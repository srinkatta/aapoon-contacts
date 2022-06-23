from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action


from contact.models import Contact
from contact.api.serializers import ContactSerializer, ContactDeleteSerializer
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

    @action(
        detail=True,
        methods=["post"],
        url_path="delete",
        permission_classes=[
            permissions.AllowAny,
        ],
        serializer_class=ContactDeleteSerializer,
    )
    def bulk_delete(self, request, pk, *args, **kwargs):
        results = []
        if pk == "bulk":
            list_data = request.data
            for i, item in enumerate(list_data):
                Contacts().delete_contact(
                    item["userid"],
                    item["contact_phone_number"],
                )
                data = {
                    "index": i,
                    "data": item,
                    "message": "Contact deleted successfully",
                }
                results.append(data)
            return Response(results)
        else:
            data = {"message": "bulk not persent in url"}
            return Response(results)
