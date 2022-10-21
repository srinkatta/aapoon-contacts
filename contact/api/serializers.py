from datetime import datetime

from rest_framework import serializers

from contact.models import Contact

ACTIONS = [
    ("UPDATE_NAME", "UPDATE_NAME"),
    ("UPDATE_PHONE", "UPDATE_PHONE"),
    ("ADD_CONTACT", "ADD_CONTACT"),
]


class ContactDetailSerializer(serializers.Serializer):
    contactName = serializers.CharField(required=False)
    contactPhoneNumber = serializers.CharField()


class ContactSerializer(serializers.Serializer):
    userid = serializers.CharField()
    UserFcmToken = serializers.CharField()
    contacts = ContactDetailSerializer(many=True)


class ContactDeleteSerializer(serializers.Serializer):
    userid = serializers.CharField()
    contact_country_code = serializers.CharField()
    contact_phone_number = serializers.CharField()
