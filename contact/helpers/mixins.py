import requests
from contact.services.db import Contacts
from contact.helpers.service import call_friend_app

from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from aapooncontact.settings import aapoon_BASE_URL


class BulkCreateContactMixin(CreateModelMixin, UpdateModelMixin):
    """
    Either create a single or many model instances in bulk by using the
    Serializer's ``many=True``

    .. note::
        This mixin uses the same method to create model instances
        as ``CreateModelMixin`` because both non-bulk and bulk
        requests will use ``POST`` request method.
    """

    def create_contact_at_dynamoDB(self, data):
        return Contacts().add_contact(data)

    def update_contact_at_dynamoDB(self, data):
        return Contacts().update_contact(data)

    def prepare_add_contact_data(self, data):
        if "action" in data:
            del data["action"]
        if "contactOldCountryCode" in data["contact"]:
            del data["contact"]["contactOldCountryCode"]
        if "contactOldPhoneNumber" in data["contact"]:
            del data["contact"]["contactOldPhoneNumber"]
        return data

    def create(self, request, *args, **kwargs):
        bulk = isinstance(request.data, list)
        if not bulk:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                data = {
                    "index": i,
                    "data": serializer.data,
                }
                if serializer.data["action"] == "UPDATE_PHONE":
                    Contacts().update_contact(serializer.data)
                    data["message"] = "Contact phone updated successfully"

                elif serializer.data["action"] == "UPDATE_NAME":
                    Contacts().update_contact_name(serializer.data)
                    data["message"] = "Contact name updated successfully"

                else:
                    data = self.prepare_add_contact_data(serializer.data)
                    Contacts().add_contact(data)
                    data["message"] = "Contact added successfully"

                return Response(data)
            else:
                data = {
                    "data": serializer.errors,
                    "message": "Error",
                }
                return Response(data)
        else:
            self.renderer_classes = (JSONRenderer,)
            request.accepted_renderer = JSONRenderer()
            list_data = request.data
            results = []
            for i, item in enumerate(list_data):
                serializer = self.get_serializer(data=item)
                if serializer.is_valid():
                    data = {
                        "index": i,
                        "data": serializer.data,
                    }
                    if serializer.data["action"] == "UPDATE_PHONE":
                        Contacts().update_contact(serializer.data)
                        data["message"] = "Contact phone updated successfully"

                    elif serializer.data["action"] == "UPDATE_NAME":
                        Contacts().update_contact_name(serializer.data)
                        data["message"] = "Contact name updated successfully"

                    else:
                        data = self.prepare_add_contact_data(serializer.data)
                        Contacts().add_contact(data)
                        data["message"] = "Contact added successfully"

                    results.append(data)
                else:
                    data = {"index": i, "message": "error", "error": serializer.errors}
                    results.append(data)
            status, message = call_friend_app(list_data)
            return Response(results)

    def update(self, request, pk, *args, **kwargs):
        """
        id = "bulk" in order to update contacts in bulk.
        """
        if pk == "bulk":
            self.renderer_classes = (JSONRenderer,)
            request.accepted_renderer = JSONRenderer()
            list_data = request.data
            results = []
            for i, item in enumerate(list_data):
                if item["action"] == "UPDATE_PHONE":
                    Contacts().update_contact(item)
                elif item["action"] == "UPDATE_NAME":
                    Contacts().update_contact_name(item)

                data = {
                    "index": i,
                    "data": item,
                    "message": "Contact updated successfully",
                }
                results.append(data)
            return Response(results)
        else:
            data = {"message": "bulk not persent in url"}
            return Response(results)
