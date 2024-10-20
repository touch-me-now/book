from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=300, required=True, validators=[UnicodeUsernameValidator()])
    password = serializers.CharField(min_length=8, validators=[validate_password], write_only=True, required=True)

    def update(self, instance, validated_data):
        raise NotImplementedError('`update()` must be implemented.')

    def create(self, validated_data):
        user_model = get_user_model()

        username = validated_data['username']
        if user_model.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': _('Already exists!')})

        user = user_model.objects.create_user(
            username=username,
            password=validated_data['password'],
        )
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
