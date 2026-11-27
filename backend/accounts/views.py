from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from .models import Address
from .serializers import(
    RegisterSerializer,
    ProfileSerializer,
    AddressSerializer
)

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from cart.services import merge_guest_cart

# 1. Customer Registration
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class LogoutView(APIView):
    def post(self,request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error":"Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message":"Successfully logged out."},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"error":"Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):

        # Generate access and refresh tokens normally
        data = super().validate(attrs)

        # Get the current request.
        request = self.context["request"]

        # Get the guest session key before it is lost
        session_key = request.session.session_key

        # Merge guest cart after successful authentication
        cart_merge = merge_guest_cart(
            user=self.user,
            session_key=session_key,
        )

        # Include merge information in the login response
        data["cart_merge"] = cart_merge

        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer 