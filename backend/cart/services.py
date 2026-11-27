from django.db import transaction
from .models import Cart, CartItem

@transaction.atomic
def merge_guest_cart(user, session_key):
    """
    Merge a guest cart into the logged in user's active cart
    """

    result = {
        "merged":False,
        "message": "No guest cart found",
        "warnings":[],
    }

    if not session_key:
        return result

    # 1. Find and lock the user cart
    guest_cart= (
        Cart.objects.select_for_update()
        .filter(
            session_key=session_key,
            status="ACTIVE",
            user__isnull=True
        )
        .first()
    )

    if not guest_cart:
        return result

    # 2. Find the users active cart
    user_cart = (
        Cart.objects.select_for_update()
        .filter(user=user, status="ACTIVE")
        .first()
    )

    # Create the active cart if the user does not have one.
    if not user_cart:
        user_cart = Cart.objects.create(user=user)

    # 3. Process each guest cart item.
    guest_items = guest_cart.items.select_related(
        "variant",
        "variant__product",
    ).all()

    for guest_item in guest_items:

        variant=guest_item.variant

        # Do not merge inactive products or variants
        if not variant.is_active or not variant.product.is_active:
            result["warning"].append(
                f"{variant.sku} was not added because it is inactive."
            )
            continue

        # Check whether this variant already exists in the user's cart
        user_item = (
            CartItem.objects.select_for_update()
            .filter(cart=user_cart, variant=variant)
            .first()
        )

        current_quantity = user_item.quantity if user_item else 0

        available_quantity = max(
            variant.stock_quantity - current_quantity,
            0
        )

        quantity_to_add = min(
            guest_item.quantity,
            available_quantity,
        )

        if quantity_to_add == 0:
            result["warning"].append(
                f"{variant.sku} was not added because no stock is available."
            )

            continue

        # 4.Add or combine quantity 
        if user_item:
            user_item.quantity += quantity_to_add
            user_item.save(update_fields=["quantity", "updated_at"])
        else:
            CartItem.objects.create(
                cart= user_cart,
                variant=variant,
                quantity = quantity_to_add,
            )

        if quantity_to_add < guest_item.quantity:
            result["warning"].append(
                f"Only {quantity_to_add} units of {variant.sku} "
                "were added because of stock limitations."
            )

        # 5. Archive the guest cart and associate with the user.
        guest_cart.user = user
        guest_cart.session_key = None
        guest_cart.status = "ABANDONED"
        guest_cart.save(
            update_fields=["user","session_key","status","updated_at"]
        )

        result["merged"]= True
        result["message"] = "Guest cart processed successfully"

        return result