from django.db import models
from django.core.validators import MinValueValidator


class Payment(models.Model):
    PAYMENT_STATUSES = [
        ("INITIATED", "Initiated"),
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    PAYMENT_METHODS = [
        ("COD", "Cash on delivery"),
        ("CARD", "Card"),
        ("UPI", "UPI"),
        ("NETBANKING", "Net banking"),
        ("WALLET", "Wallet"),
    ]

    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="payments")
    provider = models.CharField(max_length=80, blank=True)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=150, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(max_length=10, choices=PAYMENT_STATUSES, default="INITIATED")
    gateway_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["order", "status"])]

    def __str__(self):
        return f"Payment {self.pk} - {self.order.order_number}"
