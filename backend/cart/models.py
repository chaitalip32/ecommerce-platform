from django.conf import settings
from django.db import models
from django.db.models import Q


class Cart(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("CONVERTED", "Converted to order"),
        ("ABANDONED", "Abandoned"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name="carts",
    )
    # Used to identify an anonymous visitor's cart.
    session_key = models.CharField(max_length=100, null=True, blank=True, unique=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(user__isnull=False) | Q(session_key__isnull=False),
                name="cart_has_user_or_session",
            )
        ]

    def __str__(self):
        return f"Cart {self.pk}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        "catalog.ProductVariant", on_delete=models.PROTECT, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "variant"], name="unique_variant_per_cart"),
            models.CheckConstraint(condition=Q(quantity__gte=1), name="cart_item_quantity_gte_1"),
        ]

    def __str__(self):
        return f"{self.variant.sku} x {self.quantity}"
