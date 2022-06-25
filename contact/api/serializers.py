from rest_framework import serializers

from contact.models import Contact


class ContactSerializer(serializers.Serializer):
    userid = serializers.CharField()
    contact_name = serializers.CharField()
    contact_country_code = serializers.CharField()
    contact_phone_number = serializers.CharField()
    device_contact_id = serializers.CharField()


class ContactDeleteSerializer(serializers.Serializer):
    userid = serializers.CharField()
    contact_country_code = serializers.CharField()
    contact_phone_number = serializers.CharField()
