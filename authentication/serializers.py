from rest_framework import serializers


class LoginInputSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class AuthResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class MeResponseSerializer(serializers.Serializer):
    authenticated = serializers.BooleanField()
    username = serializers.CharField(required=False, allow_null=True)
