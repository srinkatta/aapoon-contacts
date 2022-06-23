from rest_framework import serializers

from contact.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class ContactDeleteSerializer(serializers.Serializer):
    userid = serializers.CharField()
    contact_phone_number = serializers.CharField()
