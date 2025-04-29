from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from utils import send_login_credentials, send_song_status_update
from media_utilities.youtube_uploader import YouTubeVideoUploader

# serializers
from administrator.serializers import GigSerializer
from artist.serializers import SongSerializer, DocumentsSerializer

# models
from administrator.models import Gig
from artist.models import Artist, Song
from form.models import Artist as FormArtist, FilmMaker
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from artist.models import Documents


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

    def delete(self, request, *args, **kwargs):
        gig = get_object_or_404(Gig, id=request.GET.get("id"))
        gig.delete()
        return Response(
            {
                "success": True,
                "message": "Gig deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


class SongMusicAPIView(APIView):
    permission_classes = [AuthenticateOnlyAdmin]

    def post(self, request, *args, **kwargs):
        if not request.data.get("id"):
            return Response(
                {
                    "success": False,
                    "message": "Song ID is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.data.get("status"):
            return Response(
                {
                    "success": False,
                    "message": "Status is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.data.get("status") == "APPROVED":
            instance = Song.objects.filter(id=request.data.get("id"))
            if not instance:
                return Response(
                    {
                        "success": False,
                        "message": "Invalid song id",
                    }
                )
            if instance.first().status == "APPROVED":
                return Response(
                    {
                        "success": False,
                        "message": "The song is already approved",
                    }
                )
            instance.update(status="APPROVED")

            # upload to youtube + send email
            uploader = YouTubeVideoUploader(
                song_instance=instance.first(),
                description="By Art39\n\n"
                "Article39 is a platform for artists to showcase their talent and get discovered.\n\n"
                "We provide a platform for artists to connect with fans and industry professionals.\n\n"
                "We help artists to promote their music and get more exposure.\n\n",
                tags=["article39", "hit music", "hit song", "music", "song"],
            )
            uploader.start()
            return Response(
                {
                    "success": True,
                    "message": "Song/Music Approved successfully. Song will be sortly availabe on YouTube",
                }
            )

        if request.data.get("status") == "REJECTED":
            instance = Song.objects.filter(id=request.data.get("id"))
            instance.update(status="REJECTED")
            # send email
            instance = instance.first()
            send_song_status_update(
                song_title=instance.title,
                user_name=instance.artist.singer_musician_info.full_name_english,
                status=instance.status,
                email=instance.artist.artist.email,
            )
            return Response(
                {
                    "success": True,
                    "message": "Song/Music Rejected. User will be notified via email.",
                }
            )

        return Response(
            {
                "success": False,
                "message": "Invalid status",
            }
        )

    def get(self, request, *args, **kwargs):

        # single song
        if request.GET.get("id"):
            song = Song.objects.filter(id=request.GET.get("id"))
            if song:
                serializer = SongSerializer(song)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"success": False, "message": "Song not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # all songs
        # filter by status
        if request.GET.get("status") == "all":
            queryset = Song.objects.all()
        elif request.GET.get("status") == "pending":
            queryset = Song.objects.filter(status="PENDING")
        elif request.GET.get("status") == "approved":
            queryset = Song.objects.filter(status="APPROVED")
        elif request.GET.get("status") == "rejected":
            queryset = Song.objects.filter(status="REJECTED")
        else:
            queryset = Song.objects.all()

        queryset = queryset.order_by("-added_at")
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = SongSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DocumentsAPIView(APIView):
    permission_classes = [AuthenticateOnlyAdmin]

    def get(self, request, *args, **kwargs):
        instances = Documents.objects.all().order_by("-updated_at")
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(instances, request)
        serializer = DocumentsSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.data.get("artist-id"):
            return Response(
                {
                    "success": False,
                    "message": "Artist ID is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.data.get("documents"):
            return Response(
                {
                    "success": False,
                    "message": "Document is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            artist_info = FormArtist.objects.get(id=request.data.get("artist-id"))
        except FormArtist.DoesNotExist:
            try:
                artist_info = FilmMaker.objects.get(id=request.data.get("artist-id"))
            except FilmMaker.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "message": "Artist not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        # check if the artist already has an account
        if hasattr(artist_info, "artist_info") or hasattr(
            artist_info, "filmmaker_info"
        ):
            # serialize the document
            serializer = DocumentsSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                if artist_info.artist_info:
                    print(artist_info.artist_info.artist.email)

                    # update or create
                    Documents.objects.update_or_create(
                        artist=artist_info.artist_info,
                        defaults={
                            "documents": serializer.validated_data.get("documents"),
                        },
                    )

                elif artist_info.filmmaker_info:
                    # check if the document already exists
                    if artist_info.filmmaker_info:
                        # update or create
                        Documents.objects.update_or_create(
                            artist=artist_info.filmmaker_info,
                            defaults={
                                "documents": serializer.validated_data.get("documents"),
                            },
                        )

            return Response(
                {
                    "success": True,
                    "message": f"Document uploaded successfully.",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": f"Artist account not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
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
        if hasattr(artist_info, "artist_info") or hasattr(
            artist_info, "filmmaker_info"
        ):
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
