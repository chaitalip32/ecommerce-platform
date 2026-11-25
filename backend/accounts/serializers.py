from rest_framework import serializers
from .models import User, Address

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only = True,
        min_length = 8
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "password",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields =[
            "id",
            "email",
            "first_name",
            "last_name",
            "phone"
        ]

        read_only_fields = ["id"]

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["id","user","created_at","updated_at"]