from rest_framework import serializers
from .models import *

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source ="variant.product.name",
        read_only = True
    )

    sku = serializers.CharField(
        source= "variant.sku",
        read_only= True
    )

    price = serializers.DecimalField(
            source= "variant.price",
            max_digits=12,
            decimal_places=2,
            read_only= True
    )

    class Meta:
        model = CartItem

        fields = [
            "id",
            "variant",
            "product_name",
            "sku",
            "price",
            "quantity",
            "added_at",
            "updated_at"
        ]

        read_only_fields = [
            "id",
            "added_at",
            "updated_at"
        ]

    def validate_quantity(self, value):

        if value < 1:
            raise serializers.ValidationError(
                "Quantity must be at least 1."
            )
        
        return value

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model=Cart

        fields=[
            "id",
            "status",
            "items",
            "created_at",
            "updated_at",
        ]

        read_only_fields=["id","status","created_at","updated_at"]