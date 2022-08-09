from datetime import datetime
from rest_framework import serializers

from contact.models import Contact


ACTIONS = [
    ("UPDATE_NAME", "UPDATE_NAME"),
    ("UPDATE_PHONE", "UPDATE_PHONE"),
    ("ADD_CONTACT", "ADD_CONTACT"),
]


class ContactDetailSerializer(serializers.Serializer):
    contactId = serializers.CharField()
    contactName = serializers.CharField()
    contactCountryCode = serializers.CharField()
    contactPhoneNumber = serializers.CharField()
    contactOldCountryCode = serializers.CharField(required=False, allow_null=True)
    contactOldPhoneNumber = serializers.CharField(required=False, allow_null=True)


class ContactSerializer(serializers.Serializer):
    userid = serializers.CharField()
    UserFcmToken = serializers.CharField()
    action = serializers.ChoiceField(choices=ACTIONS, default="ADD_CONTACT")
    contact = ContactDetailSerializer()


class ContactDeleteSerializer(serializers.Serializer):
    userid = serializers.CharField()
    contact_country_code = serializers.CharField()
    contact_phone_number = serializers.CharField()
