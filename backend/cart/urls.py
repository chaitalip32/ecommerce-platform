from django.urls import path
from .views import AddToCartView

urlpatterns = [
    path("items/", AddToCartView.as_view(), name="add-to-cart"),    
]