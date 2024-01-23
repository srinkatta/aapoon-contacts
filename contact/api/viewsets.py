from django.db import connections
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from contact.api.serializers import ContactDeleteSerializer, ContactSerializer
from contact.helpers.mixins import BulkCreateContactMixin
from contact.models import Contact
from contact.services.db import Contacts
from contact.services.events import ContactsEvents


class ContactViewSet(BulkCreateContactMixin, viewsets.ModelViewSet):
    """
    Viewset for Contact Model
    In order to perform actions in bulk, send an array or list of objects with the given payload on every endpoint
    """

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny | HasAPIKey]
    http_method_names = ("get", "post", "put")

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="userid",
                description="Filter the Contacts by User Id",
                required=True,
                type=int,
            ),
        ]
    )
    def list(self, request):
        import sys
        python_version = sys.version   # Todo remove after python version verify
        logger.info(f"Python Version from logger: {python_version}")
        user_id = request.GET.get("userid", "")
        if not user_id:
            return Response({"data": "userid required in params"})
        contacts = Contacts().list_contacts(user_id)
        return Response(contacts)

    @action(
        detail=True,
        methods=["post"],
        url_path="delete",
        permission_classes=[
            permissions.AllowAny,
        ],
        serializer_class=ContactSerializer,
    )
    def bulk_delete(self, request, pk, *args, **kwargs):
        """
        id = "bulk" in order to delete contacts in bulk.
        """
        results = []
        if pk == "bulk":
            list_data = request.data
            for i, item in enumerate(list_data):
                Contacts().delete_contact(
                    item,
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

    @action(
        detail=False,
        methods=["post"],
        url_path=r"queue",
        permission_classes=[permissions.AllowAny | HasAPIKey],
        serializer_class=ContactSerializer,
    )
    def contacts_queue(self, request, *args, **kwargs):
        """
        Add contacts payload to queue
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ContactsEvents().create_event(serializer.data)
        return Response(
            {"data": "Contacts added to queue successfully."},
            status=status.HTTP_200_OK,
        )
