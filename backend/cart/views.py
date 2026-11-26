from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import Cart,CartItem
from .serializer import CartSerializer, CartItemSerializer
from catalog.models import ProductVariant

class AddToCartView(APIView):

    permission_classes=[AllowAny]

    def post(self, request):

        # 1. Getting variant and product quantity from request
        variant_id = request.data.get("variant")
        quantity = request.data.get("quantity", 1)

        if not variant_id:
            return Response(
                {"error": "Product variant is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. validate quantity
        try:
            quantity=int(quantity)
            if quantity < 1:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "Quantity must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Check whether the variant is exists and is active
        try:
            variant = ProductVariant.objects.select_related(
                "product"
            ).get(
                id=variant_id,
                is_active = True,
                product__is_active=True
            )
        except ProductVariant.DoesNotExist:
            return Response(
                {"error": "Product variant not found or inactive."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 4. Identify the customer and get/create cart
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                status="ACTIVE",
                defaults={"session_key":None}
            )

        else:
            # Create a django session if one does not exist
            if not request.session.session_key:
                request.session.create()

            session_key=request.session.session_key

            cart, created=Cart.objects.get_or_create(
                session_key=session_key,
                status="ACTIVE",
                defaults={"user":None}
            )

        # 5. Add item or update existing item
        with transaction.atomic():

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                variant=variant,
                defaults={"quantity":quantity}
            )

            if not created:
                cart_item.quantity += quantity

            # 6. Check stock availability 
            if cart_item.quantity > variant.stock_quantity:
                return Response(
                    {
                        "error":(
                            f"Only {variant.stock_quantity} units "
                            "are currently available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item.save()

        # 7. Return the updated cart item
        serializer = CartItemSerializer(cart_item)

        return Response(
            {
                "message": "Item added to cart successfully.",
                "cart_item": serializer.data
            },
            status= status.HTTP_201_CREATED
        )