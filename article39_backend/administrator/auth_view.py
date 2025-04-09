from django.shortcuts import render
from dj_rest_auth.registration.views import LoginView
from django.contrib.auth import login as django_login
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from dj_rest_auth.views import PasswordChangeView
from administrator.serializers import CustomPasswordChangeSerializer
from rest_framework import status

# authentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class LoginWthPermission(APIView):
    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        self.login()

        if self.user.is_agent:
            if self.user.agent.approved:
                django_login(self.request, self.user)
            else:
                return Response({"error": "Your account has not been approved"})

        return self.get_response()

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response(
                {"success": False, "message": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.is_artist and not user.artist_profile.is_verified:
            return Response(
                {
                    "success": False,
                    "message": "Your account is deactivated, please contact admin",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Construct the response
        response_data = {
            "success": True,
            "access": access_token,
            "refresh": str(refresh),
            "user": {
                "pk": user.pk,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "role": "ARTIST" if user.is_artist else "ADMIN",
        }

        return Response(response_data, status=status.HTTP_200_OK)


# change password
class CustomPasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomPasswordChangeSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            # Check if old password is correct
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"old_password": "Old password is incorrect."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Set the new password
            user.set_password(serializer.validated_data["new_password1"])
            user.save()

            return Response(
                {"detail": "Password has been changed successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
