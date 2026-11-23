import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator


class Order(models.Model):
    ORDER_STATUSES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("PROCESSING", "Processing"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
        ("REFUNDED", "Refunded"),
    ]
    PAYMENT_STATUSES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("PARTIALLY_REFUNDED", "Partially refunded"),
        ("REFUNDED", "Refunded"),
    ]

    order_number = models.CharField(max_length=32, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="orders",
    )
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=15, choices=ORDER_STATUSES, default="PENDING")
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUSES, default="PENDING"
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    coupon = models.ForeignKey(
        "promotions.Coupon", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="orders",
    )
    # Immutable checkout-time snapshots; do not rely on a customer's editable address.
    shipping_address = models.JSONField()
    billing_address = models.JSONField(null=True, blank=True)
    customer_note = models.TextField(blank=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-placed_at"]
        indexes = [
            models.Index(fields=["user", "placed_at"]),
            models.Index(fields=["status", "placed_at"]),
            models.Index(fields=["payment_status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = uuid.uuid4().hex[:16].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        "catalog.ProductVariant", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="order_items",
    )
    product_name = models.CharField(max_length=200)
    sku = models.CharField(max_length=80)
    variant_name = models.CharField(max_length=120, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    line_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
