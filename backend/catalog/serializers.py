from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields=[
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "image",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["id", "slug", "created_at", "updated_at"]

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product

        fields=[
            'id',
            'name',
            'slug',
            'category',
            'brand',
            'short_description',
            'description',
            'is_active',
            'is_featured',
            'created_at',
            'updated_at',
        ]

        read_only_fields=['id', 'slug', 'created_at', 'updated_at']

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage

        fields=[
            'id',
            'product',
            'image',
            'alt_text',
            'is_primary',
            'display_order',
        ]

        read_only_fields=['id']

        def validate(self, attrs):
            product=attrs.get(
                "product",
                getattr(self.instance, "product", None)
            )

            is_primary = attrs.get(
                "is_primary",
                getattr(self.instance, "is_primary", False)
            )

            if is_primary and product:
                existing_primary = ProductImage.objects.filter(
                    product=product,
                    is_primary=True
                )

                if self.isinstance:
                    existing_primary = existing_primary.exclude(
                        pk=self.isinstance.pk
                    )

                if existing_primary.exists():
                    raise serializers.ValidationError({
                        "is_primary": "This product already has a primary image"
                    })
            
            return attrs

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant

        fields=[
            "id",
            "product",
            "sku",
            "variant_name",
            "attributes",
            "price",
            "compare_at_price",
            "stock_quantity",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields=["id","created_at","updated_at"]

        def validate(self, attrs):

            price=attrs.get(
                "price",
                getattr(self.instance,"price",None)
            )

            compare_at_price = attrs.get(
                "compare_at_price",
                getattr(self.isinstance,"compare_at_price",None)
            )

            if(
                compare_at_price is not None
               and price is not None
               and compare_at_price < price
            ):
                raise serializers.ValidationError({
                    "compare_at_price":
                    "compare-at price must be greater that equal to selling price"
                })
            
            return attrs