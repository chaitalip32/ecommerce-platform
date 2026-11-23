from django.db import models


class Shipment(models.Model):
    SHIPMENT_STATUSES = [
        ("PENDING", "Pending"),
        ("PACKED", "Packed"),
        ("SHIPPED", "Shipped"),
        ("IN_TRANSIT", "In transit"),
        ("OUT_FOR_DELIVERY", "Out for delivery"),
        ("DELIVERED", "Delivered"),
        ("FAILED", "Delivery failed"),
        ("RETURNED", "Returned"),
    ]

    order = models.OneToOneField("orders.Order", on_delete=models.PROTECT, related_name="shipment")
    carrier = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=120, blank=True)
    tracking_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=SHIPMENT_STATUSES, default="PENDING")
    shipped_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment for {self.order.order_number}"
