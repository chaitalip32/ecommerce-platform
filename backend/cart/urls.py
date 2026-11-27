from django.urls import path
from .views import AddToCartView, ViewCartView, UpdateCartItemView, RemoveCartItemView, ClearCartView

urlpatterns = [
    path("items/", AddToCartView.as_view(), name="add-to-cart"),    
    path("", ViewCartView.as_view(), name="view-cart"),
    path("items/<int:item_id>/", UpdateCartItemView.as_view(), name="update-cart-item"),
    path(
        "items/<int:item_id>/remove/",
        RemoveCartItemView.as_view(),
        name="remove-cart-item"
    ),
    path("clear/", ClearCartView.as_view(), name="clear-cart"),
    
]