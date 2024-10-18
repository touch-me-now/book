from rest_framework import generics

from accounts.serializers import RegistrationSerializer


class RegistrationView(generics.CreateAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = RegistrationSerializer

