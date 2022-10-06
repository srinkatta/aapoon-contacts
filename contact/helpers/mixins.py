import requests
from django.conf import settings
from django.db import connections
from pyfcm import FCMNotification
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from aapooncontact.settings import aapoon_BASE_URL
from contact.helpers.service import call_friend_app
from contact.services.db import Contacts
from contact.services.events import ContactsEvents


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

    def prepare_xmpp_query_value(self, row):
        self.fcm_token = row["UserFcmToken"]
        contact = row["contact"]
        phone_number = f"{contact['contactCountryCode']}{contact['contactPhoneNumber']}"
        jid = f"{phone_number}@{settings.XMPP_HOST}"
        value = (
            f"{phone_number}",
            f"{jid}",
            f"{contact['contactName']}",
            "B",
            "N",
            "",
            "N",
            "",
            "item",
        )
        return value

    def execute_xmpp_query(self, query):
        print(query)
        with connections["xmpp"].cursor() as cursor:
            cursor.execute(query)

    def __trigger_notification(self):
        push_service = FCMNotification(api_key=settings.FCM_API_KEY)
        message_title = "Contact Sync complete"
        message_body = f"Hi there, contact sync was completed successfully"
        result = push_service.notify_single_device(
            registration_id=self.fcm_token,
            message_title=message_title,
            message_body=message_body,
        )
        print(result)

    def create(self, request, *args, **kwargs):
        values = []
        query = "INSERT INTO rosterusers (username, jid, nick, subscription, ask, askmessage, server, subscribe, type) VALUES "
        bulk = isinstance(request.data, list)
        if not bulk:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                value = self.prepare_xmpp_query_value(serializer.data)
                values = value
                data = {
                    "data": serializer.data,
                }
            else:
                data = {
                    "data": serializer.errors,
                    "message": "Error",
                }
            query = f"{query}{tuple(values)}"
            self.execute_xmpp_query(query)
            self.__trigger_notification()
            return Response(data)
        else:
            self.renderer_classes = (JSONRenderer,)
            request.accepted_renderer = JSONRenderer()
            list_data = request.data
            results = []
            for i, item in enumerate(list_data):
                serializer = self.get_serializer(data=item)
                if serializer.is_valid():
                    print(serializer.data)
                    value = self.prepare_xmpp_query_value(serializer.data)
                    values.append(value)
                    data = {
                        "index": i,
                        "data": serializer.data,
                    }
                    results.append(data)
                else:
                    data = {"index": i, "message": "error", "error": serializer.errors}
                    results.append(data)

            values = str(values).replace("[", "")
            values = str(values).replace("]", "")
            query = f"{query}{values}"
            self.execute_xmpp_query(query)
            self.__trigger_notification()
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
