import requests
from django.conf import settings
from django.db import connections
from pyfcm import FCMNotification
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from aapooncontact.settings import aapoon_BASE_URL
from contact.helpers.utils import check_friend_status
from contact.services.db import Contacts


class RosterUser(object):
    def __init__(self, **kwargs):
        for field in (
            "username",
            "jid",
            "nick",
            "subscription",
            "ask",
            "askmessage",
            "server",
            "subscribe",
            "type",
        ):
            setattr(self, field, kwargs.get(field, None))

    def __str__(self):
        return f"RosterUser(username={str(self.username)} ,jid={self.jid}, nick={self.nick})"

    def __repr__(self):
        return f"RosterUser(username={str(self.username)} ,jid={self.jid}, nick={self.nick})"


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
        contacts = row["contacts"]
        username = row["userid"]
        user_jid = f"{username}@{settings.XMPP_HOST}"
        query = f"select * from rosterusers where username='{username}'"
        users = self.fetch_rosteruser(query)

        for contact in contacts:
            contact_phone_number = contact['contactPhoneNumber']
            contact_jid = f"{contact_phone_number}@{settings.XMPP_HOST}"
            nick = contact["contactName"]
            contact_roster = {"username": username, "jid": contact_jid}

            if contact_roster in users:
                query = f"Update rosterusers set subscription = 'B', nick = '{nick}' where  username = '{username}' and jid = '{contact_jid}'"
                self.execute_xmpp_query(query)
                query = f"Update rosterusers set subscription = 'B' where  username = '{contact_phone_number}' and jid = '{user_jid}'"
                self.execute_xmpp_query(query)
            else:
                status, response = check_friend_status(contact_phone_number)
                askmessage = ""
                if response["aapoonUser"]:
                    nick = f"{nick}-aapoon"
                    askmessage = "aapoon"

                user_query = (
                    f"{username}",
                    f"{contact_jid}",
                    f"{nick}",
                    "T",
                    "N",
                    f"{askmessage}",
                    "N",
                    "",
                    "item",
                )
                roaster_query = (
                    f"{contact_phone_number}",
                    f"{user_jid}",
                    "",
                    "F",
                    "N",
                    f"{askmessage}",
                    "N",
                    "",
                    "item",
                )
                self.values.append(user_query)
                self.values.append(roaster_query)

    def fetch_rosteruser(self, query):
        with connections["xmpp"].cursor() as cursor:
            response = cursor.execute(query)
            user_data = cursor.fetchall()
            user_data = sorted(user_data, key=lambda x: x[0])
            users = [{"username": user[0], "jid": user[1]} for user in user_data]
            return users

        return []

    def execute_xmpp_query(self, query):
        print(query)
        with connections["xmpp"].cursor() as cursor:
            cursor.execute(query)

    def __trigger_notification(self):
        push_service = FCMNotification(api_key=settings.FCM_API_KEY)
        message_title = "Contact Sync complete"
        data_message = {
        "identifier": "ContactSync",
        "body" : "Hi there, contact sync was completed successfully"
        }
        message_body = f"Hi there, contact sync was completed successfully"
        result = push_service.notify_single_device(
            registration_id=self.fcm_token, data_message=data_message
        )
        print(result)

    def create(self, request, *args, **kwargs):
        self.values = []
        query = "INSERT INTO rosterusers (username, jid, nick, subscription, ask, askmessage, server, subscribe, type) VALUES "
        print("Event trigger to the Contact API")
        print(request.data)
        bulk = isinstance(request.data, list)
        if not bulk:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.prepare_xmpp_query_value(serializer.data)
                data = {
                    "data": serializer.data,
                }
            else:
                data = {
                    "data": serializer.errors,
                    "message": "Error",
                }

            if self.values:
                self.values = str(self.values).replace("[", "")
                self.values = str(self.values).replace("]", "")
                query = f"{query}{self.values}"
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
                    self.prepare_xmpp_query_value(serializer.data)
                    data = {
                        "index": i,
                        "data": serializer.data,
                    }
                    results.append(data)
                else:
                    data = {"index": i, "message": "error", "error": serializer.errors}
                    results.append(data)

            if self.values:
                self.values = str(self.values).replace("[", "")
                self.values = str(self.values).replace("]", "")
                query = f"{query}{self.values}"
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
