from rest_framework import serializers

from contact.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        exclude = ("friend",)


class ContactDeleteSerializer(serializers.Serializer):
    userid = serializers.CharField()
    contact_phone_number = serializers.CharField()
