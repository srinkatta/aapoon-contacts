from rest_framework import permissions, viewsets


from contact.models import Contact
from contact.api.serializers import ContactSerializer


class ContactViewSet(viewsets.ModelViewSet):
    """
    Viewset for Contact Model
    """

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (permissions.AllowAny,)
