import requests
from contact.services.db import Contacts

from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from aapooncontact.settings import friend_BASE_URL


class BulkCreateContactMixin(CreateModelMixin, UpdateModelMixin):
    """
    Either create a single or many model instances in bulk by using the
    Serializer's ``many=True``

    .. note::
        This mixin uses the same method to create model instances
        as ``CreateModelMixin`` because both non-bulk and bulk
        requests will use ``POST`` request method.
    """

    def create_contact_at_dynamoDB(self, serializer):
        data = {
            "userid": f"{serializer.data['userid']}",
            "device_contact_id": f"{serializer.data['device_contact_id']}",
            "contact_name": f"{serializer.data['contact_name']}",
            "contact_phone_number": f"{serializer.data['contact_phone_number']}",
            "contact_country_code": f"{serializer.data['contact_country_code']}",
        }
        return Contacts().add_contact(data)

    def update_contact_at_dynamoDB(self, userid, country_code, phone_number, item):
        data = {
            "contact_country_code": f"{item['contact_country_code']}",
            "contact_phone_number": f"{item['contact_phone_number']}",
            "device_contact_id": f"{item['device_contact_id']}",
            "contact_name": f"{item['contact_name']}",
        }
        return Contacts().update_contact(userid, country_code, phone_number, data)

    def create(self, request, *args, **kwargs):
        bulk = isinstance(request.data, list)
        if not bulk:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                try:
                    self.update_contact_at_dynamoDB(
                        serializer.data["userid"],
                        serializer.data["contact_country_code"],
                        serializer.data["contact_phone_number"],
                        serializer.data,
                    )
                except Exception:
                    self.create_contact_at_dynamoDB(serializer)
                    data = {
                        "data": serializer.data,
                        "message": "Contact added successfully",
                    }
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
                    try:
                        self.update_contact_at_dynamoDB(
                            serializer.data["userid"],
                            serializer.data["contact_country_code"],
                            serializer.data["contact_phone_number"],
                            serializer.data,
                        )
                    except Exception:
                        self.create_contact_at_dynamoDB(serializer)
                        data = {
                            "index": i,
                            "data": serializer.data,
                            "message": "Contact added successfully",
                        }
                        results.append(data)
                else:
                    data = {"index": i, "message": "error", "error": serializer.errors}
                    results.append(data)
            self.call_friend_app(results)
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

                self.update_contact_at_dynamoDB(
                    item["userid"],
                    item["contact_country_code"],
                    item["contact_phone_number"],
                    item,
                )
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

    def call_friend_app(data):
        url = f"{friend_BASE_URL}/api/friends/check/"
        headers = {}
        result = requests.post(url, data=data, headers=headers)
        if result.status_code == 200:
            return 200, result.json()
        return 400, result.text
