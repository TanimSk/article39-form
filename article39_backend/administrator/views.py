from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from utils import send_login_credentials

# serializers
from administrator.serializers import GigSerializer

# models
from administrator.models import Gig
from artist.models import Artist
from form.models import Artist as FormArtist, FilmMaker
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string


# Pagination Config
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
    page_query_param = "p"


# Authenticate User Only Class
class AuthenticateOnlyAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_admin:
                return True
            else:
                return False
        return False


class GigAPIView(APIView):
    permission_classes = [AuthenticateOnlyAdmin]
    serializer = GigSerializer

    def get(self, request, *args, **kwargs):
        queryset = Gig.objects.all().order_by("-datetime")
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Gig created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

    def put(self, request, *args, **kwargs):
        gig = get_object_or_404(Gig, id=request.data.get("id"))
        serializer = self.serializer(gig, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "Gig updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# verify artist account
class CreateArtistAccountAPIView(APIView):
    """
    On verification of artist, an account will be created for him.
    and login credentials will be sent to the artist email.
    """

    permission_classes = [AuthenticateOnlyAdmin]

    def post(self, request, *args, **kwargs):

        # validate the request data
        if not request.data.get("id"):
            return Response(
                {
                    "success": False,
                    "message": "Artist ID is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not "verified" in request.data:
            return Response(
                {
                    "success": False,
                    "message": "Verified status is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            artist_info = FormArtist.objects.get(id=request.data.get("id"))
        except FormArtist.DoesNotExist:
            try:
                artist_info = FilmMaker.objects.get(id=request.data.get("id"))
            except FilmMaker.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "message": "Artist not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        # check if the artist already has an account
        if artist_info.artist_info or artist_info.filmmaker_info:
            if artist_info.artist_info:
                artist_info.artist_info.is_verified = request.data.get("verified")
                artist_info.artist_info.save()

            elif artist_info.filmmaker_info:
                artist_info.filmmaker_info.is_verified = request.data.get("verified")
                artist_info.filmmaker_info.save()

            return Response(
                {
                    "success": False,
                    "message": f"Artist account {'activated' if request.data.get('verified') else 'deactivated'} successfully.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_instance = get_user_model()
        random_password = get_random_string(length=6)  # adjust length if needed

        # check if the model is artist or filmmaker
        if isinstance(artist_info, FormArtist):
            # Create the user
            user = user_instance.objects.create_user(
                username=artist_info.email,
                email=artist_info.email,
                password=random_password,
                is_artist=True,
            )
            Artist.objects.create(
                artist=user,
                singer_musician_info=artist_info,
                is_verified=True,
            )

            send_login_credentials(
                email=artist_info.email,
                password=random_password,
                username=artist_info.full_name_english,
            )

        elif isinstance(artist_info, FilmMaker):
            # Create the user
            user = user_instance.objects.create_user(
                username=artist_info.basic_info.get("full_name_en"),
                email=artist_info.basic_info.get("email"),
                password=random_password,
                is_artist=True,
            )
            Artist.objects.create(
                artist=user,
                filmmaker_info=artist_info,
                is_verified=True,
            )
            send_login_credentials(
                email=artist_info.basic_info.get("email"),
                password=random_password,
                username=artist_info.basic_info.get("full_name_en"),
            )

        return Response(
            {
                "success": True,
                "message": "Artist account verified and created successfully. Artists login credentials have been sent to the email.",
            },
            status=status.HTTP_201_CREATED,
        )
