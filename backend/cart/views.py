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

class ViewCartView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        # 1. Identify the customer's cart
        if request.user.is_authenticated:

            cart = Cart.objects.filter(
                user = request.user,
                status = "ACTIVE"
            ).first()

        else:

            session_key = request.session.session_key

            if not session_key:
                return Response({
                    "message": "Your cart is empty.",
                    "items": [],
                    "total_items": 0,
                    "subtotal": "0.00"
                })

            cart = Cart.objects.filter(
                session_key = session_key,
                status = "ACTIVE"
            ).first()

        # 2. Handle empty cart
        if not cart:
            return Response({
                "message": "Your cart is empty",
                "items": [],
                "total_items": 0,
                "subtotal": "0.00"
            })

        # 3. Retrieve cart items
        cart_items = cart.items.select_related(
            "variant",  
            "variant__product"
        ).all()

        # 4. Serialize cart items
        serializer = CartItemSerializer(
            cart_items,
            many=True
        )

        # 5. Calculate Totals
        total_items = sum(
            item.quantity for item in cart_items
        )

        subtotal = sum(
            item.quantity * item.variant.price
            for item in cart_items
        )

        # 6. Return response
        return Response({
            "cart_id": cart.id,
            "status": cart.status,
            "items": serializer.data,
            "total_items": total_items,
            "subtotal": str(subtotal)
        })

class UpdateCartItemView(APIView):

    permission_classes = [AllowAny]

    def patch(self, request, item_id):
        # 1. Identify the customers active cart
        if request.user.is_authenticated:

            cart = Cart.objects.filter(
                user = request.user,
                status = "ACTIVE"
            ).first()

        else:

            session_key = request.session.session_key

            if not session_key:
                return Response(
                    {"error":"Cart not found."},
                    status= status.HTTP_404_NOT_FOUND
                )

            cart = Cart.objects.filter(
                session_key = session_key,
                status = "ACTIVE"
            ).first()

        if not cart:
            return Response(
                {"error":"Cart not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Find the item inside this customers cart
        cart_item = cart.items.select_related(
            "variant"
        ).filter(id=item_id).first()

        if not cart_item:
            return Response(
                {"error":"Cart not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3. Validate the new quantity
        serializer = CartItemSerializer(
            cart_item,
            data=request.data,
            partial = True
        )

        serializer.is_valid(raise_exception=True)

        new_quantity = serializer.validated_data.get(
            "quantity",
            cart_item.quantity
        )

        # 4. Check available stock
        if new_quantity > cart_item.variant.stock_quantity:
            return Response(
                {
                    "error":(
                        f"Only {cart_item.variant.stock_quantity}",
                        "units are available."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5. Save the updated quantity
        serializer.save()

        return Response(
            {
                "message": "Cart quality updated successfully.",
                "cart_item": serializer.data
            },
            status=status.HTTP_200_OK
        )


class RemoveCartItemView(APIView):

    permission_classes = [AllowAny]

    def delete(self, request, item_id):

        # 1. Identify the customer's active cart
        if request.user.is_authenticated:

            cart = Cart.objects.filter(
                user=request.user,
                status="ACTIVE"
            ).first()

        else:

            session_key = request.session.session_key

            if not session_key:
                return Response(
                    {"error": "Cart not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            cart = Cart.objects.filter(
                session_key=session_key,
                status="ACTIVE"
            ).first()

        if not cart:
            return Response(
                {"error": "Cart not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Find the item in this customer's cart
        cart_item = cart.items.filter(id=item_id).first()

        if not cart_item:
            return Response(
                {"error": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3. Delete the item
        cart_item.delete()

        return Response(
            {"message": "Item removed from cart successfully."},
            status=status.HTTP_200_OK
        )


class ClearCartView(APIView):

    permission_classes = [AllowAny]

    def delete(self, request):

        # 1. Identify the customer's active cart
        if request.user.is_authenticated:

            cart = Cart.objects.filter(
                user=request.user,
                status="ACTIVE"
            ).first()

        else:

            session_key = request.session.session_key

            if not session_key:
                return Response(
                    {"message": "Cart is already empty."},
                    status=status.HTTP_200_OK
                )

            cart = Cart.objects.filter(
                session_key=session_key,
                status="ACTIVE"
            ).first()

        # 2. Check whether cart exists
        if not cart:
            return Response(
                {"message": "Cart is already empty."},
                status=status.HTTP_200_OK
            )

        # 3. Delete all cart items
        deleted_count, _ = cart.items.all().delete()

        return Response(
            {
                "message": "Cart cleared successfully.",
                "deleted_items": deleted_count
            },
            status=status.HTTP_200_OK
        )
    
class ValidateCartView(APIView):

    permission_classes = [AllowAny]

    def post(self,request):

        # 1. Identify the customers active cart
        if request.user.is_authenticated:

            cart=Cart.objects.filter(
                user=request.user,
                status="ACTIVE"
            ).first()

        else:

            session_key = request.session.session_key

            if not session_key:
                return Response({
                    "valid": False,
                    "message": "Your cart is empty.",
                    "issues": []
                })

            cart = Cart.objects.filter(
                session_key=session_key,
                status="ACTIVE"
            ).first()

        # 2. Check whether cart exists
        if not cart:
            return Response({
                "validate": False,
                "message": "Your cart is empty.",
                "issues": []
            })

        # 3. Retrieve cart items
        cart_items = cart.items.select_related(
            "variant",
            "variant__product"
        ).all()

        if not cart_items.exists():
            return Response({
                "valid": False,
                "message": "Your cart is empty",
                "issues": []
            })

        issues= []

        # 4. Validate each cart item
        for item in cart_items:

            variant = item.variant
            product = variant.product

            # Check whether product is active
            if not product.is_active:
                issues.append({
                    "variant_id": variant.id,
                    "sku": variant.sku,
                    "issue": "Product is inactive."
                })

                continue

            # Check whether variant is active
            if not variant.is_active:
                issues.append({
                    "variant_id": variant.id,
                    "sku": variant.sku,
                    "issue": "Product variant is inactive."
                })

                continue

            # Check stock availabillity
            if item.quantity > variant.stock_quantity:
                issues.append({
                    "variant_id": variant.id,
                    "sku": variant.sku,
                    "issue": "Insufficient stock.",
                    "requested_quantity": item.quantity,
                    "available_quantity": variant.stock_quantity
                })

        # 5. Return validation result
        if issues:
            return Response({
                "valid": False,
                "message": "Some cart item needs attention.",
                "issues": issues
            })

        return Response({
            "valid": True,
            "message": "Your cart is ready for checkout",
            "issues": []
        })