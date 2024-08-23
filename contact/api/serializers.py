from datetime import datetime

from urllib.parse import urlparse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from contact.models import Contact
from common.prevent_ssrf import PreventSSRF

ACTIONS = [
    ("UPDATE_NAME", "UPDATE_NAME"),
    ("UPDATE_PHONE", "UPDATE_PHONE"),
    ("ADD_CONTACT", "ADD_CONTACT"),
]


class ContactDetailSerializer(serializers.Serializer):
    contactName = serializers.CharField(allow_blank=True, allow_null=True)
    contactPhoneNumber = serializers.CharField()


class ContactSerializer(serializers.Serializer):
    userid = serializers.CharField()
    UserFcmToken = serializers.CharField()
    contacts = ContactDetailSerializer(many=True)


class ContactDeleteSerializer(serializers.Serializer):
    userid = serializers.CharField()
    contact_country_code = serializers.CharField()
    contact_phone_number = serializers.CharField()

class ExternalRequestSerializer(serializers.Serializer):
    """
    Serializer class to validate external request
    """

    url = serializers.URLField(required=True)

    def validate_url(self, url):

        if not PreventSSRF.is_valid_url(url):
            raise ValidationError("Invalid URL")

        parsed_uri = urlparse(url)
        hostname = parsed_uri.hostname

        if not PreventSSRF.is_host_allowed(hostname):
            raise ValidationError("Host is not allowed")

        return url