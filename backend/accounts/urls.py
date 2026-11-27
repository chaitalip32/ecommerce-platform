from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LogoutView, ProfileView, AddressViewSet, CustomTokenObtainPairView

router = DefaultRouter()
router.register("addresses", AddressViewSet, basename="address")

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('',include(router.urls)),
]