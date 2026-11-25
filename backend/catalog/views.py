from django.shortcuts import render
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, ProductVariantSerializer
from .models import Category, Product, ProductImage, ProductVariant
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny

class CategoryViewSet(viewsets.ModelViewSet):

    queryset=Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [IsAdminUser()]

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset= Product.objects.select_related("category")

        # Admin users can view all products
        if self.request.user.is_staff:
            return queryset.all()

        # Public users can only view active products
        return queryset.filter(is_active=True)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [IsAdminUser()]

class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        queryset = ProductImage.objects.select_related("product")

        if self.request.user.is_staff:
            return queryset.all()

        return queryset.filter(product__is_active=True)

    def get_permissions(self):
        if self.action in ["list","retrieve"]:
            return [AllowAny()]

        return [IsAdminUser()]

class ProductVariantViewSet(viewsets.ModelViewSet):
    serializer_class = ProductVariantSerializer

    def get_queryset(self):
        queryset = ProductVariant.objects.select_related("product")

        if self.request.user.is_staff:
            return queryset.all()

        return queryset.filter(
            product__is_active = True,
            is_active=True
        )

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [IsAdminUser()]