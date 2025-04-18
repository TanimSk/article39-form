from django.shortcuts import render
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination
from administrator.models import Gig
from django.utils import timezone
from media_utilities.song_analytics_extractor import YouTubeVideoFetcher

# serializers
from artist.serializers import SongSerializer, PaymentSerializer, DocumentsSerializer
from administrator.serializers import GigSerializer

# models
from artist.models import GigApplication, Payment
from django.utils import timezone
from django.db.models import Sum


# Pagination Config
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
    page_query_param = "p"


# Authenticate User Only Class (only for artist [musician/singer])
class AuthenticateOnlyArtist(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if (
                request.user.is_artist
                and request.user.artist_profile.is_verified
                and request.user.artist_profile.singer_musician_info
            ):
                return True
            else:
                return False
        return False


class DashboardAPIView(APIView):
    permission_classes = [AuthenticateOnlyArtist]

    def get(self, request, *args, **kwargs):

        UPDATE_YOUTUBE_STATS_THRESHOLD = 10  # in seconds
        song_music_instance = request.user.artist_profile.songs.all()

        # get all uploaded songs
        uploaded_song_musics = song_music_instance.filter(
            status="APPROVED", upload_status="UPLOADED"
        ).order_by("-added_at")
        
        # check if youtube stats are updated
        if uploaded_song_musics.first().updated_at < timezone.localtime(
            timezone.now()
        ) - timezone.timedelta(seconds=UPDATE_YOUTUBE_STATS_THRESHOLD):
            # update youtube stats
            YouTubeVideoFetcher(uploaded_song_musics).start()
            print("✅ YouTube stats updated.")

        response_data = {
            "approved_song_musics": song_music_instance.filter(
                status="APPROVED"
            ).count(),
            "pending_song_musics": song_music_instance.filter(status="PENDING").count(),
            "rejected_song_musics": song_music_instance.filter(
                status="REJECTED"
            ).count(),
            "applied_gigs": GigApplication.objects.filter(
                user=request.user.artist_profile
            ).count(),
            # total likes, comments, views
            **uploaded_song_musics.aggregate(
                total_likes=Sum("youtube_like_count"),
                total_comments=Sum("youtube_comment_count"),
                total_views=Sum("youtube_view_count"),
            ),
        }

        return Response(
            {
                "success": True,
                "data": response_data,
            },
            status=status.HTTP_200_OK,
        )


class EnlistSongAPIView(APIView):
    permission_classes = [AuthenticateOnlyArtist]

    def post(self, request):
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(artist=request.user.artist_profile)
            return Response(
                {
                    "success": True,
                    "message": "Song enlisted successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):

        # single song
        if request.GET.get("id"):
            song = request.user.artist_profile.songs.filter(
                id=request.GET.get("id")
            ).first()
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
            queryset = request.user.artist_profile.songs.all()
        elif request.GET.get("status") == "pending":
            queryset = request.user.artist_profile.songs.filter(status="PENDING")
        elif request.GET.get("status") == "approved":
            queryset = request.user.artist_profile.songs.filter(status="APPROVED")
        elif request.GET.get("status") == "rejected":
            queryset = request.user.artist_profile.songs.filter(status="REJECTED")
        else:
            queryset = request.user.artist_profile.songs.all()

        queryset = queryset.order_by("-added_at")
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = SongSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def delete(self, request, *args, **kwargs):
        if not request.GET.get("id"):
            return Response(
                {"success": False, "message": "Song ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        song = request.user.artist_profile.songs.filter(
            id=request.GET.get("id")
        ).first()
        if song:
            song.delete()
            return Response(
                {"success": True, "message": "Song deleted successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"success": False, "message": "Song not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class GigAPIView(APIView):
    permission_classes = [AuthenticateOnlyArtist]

    def get(self, request, *args, **kwargs):

        gig_instances = Gig.objects.filter(
            datetime__gte=timezone.localtime(timezone.now())
        ).order_by("datetime")

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(gig_instances, request)
        serializer = GigSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    # apply for gig
    def post(self, request, *args, **kwargs):
        if not "song_id" in request.data:
            return Response(
                {"success": False, "message": "Song ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not "gig_id" in request.data:
            return Response(
                {"success": False, "message": "Gig ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check given audio is approved
        if not request.user.artist_profile.songs.filter(
            id=request.data["song_id"], status="APPROVED"
        ).exists():
            return Response(
                {
                    "success": False,
                    "message": "Audio is not approved. Please contact admin.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if already applied
        if GigApplication.objects.filter(
            user=request.user.artist_profile,
            gig_id=request.data["gig_id"],
            song_id=request.data["song_id"],
        ).exists():
            return Response(
                {"success": False, "message": "Already applied for this gig."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        GigApplication.objects.create(
            user=request.user.artist_profile,
            gig_id=request.data["gig_id"],
            song_id=request.data["song_id"],
        )
        return Response(
            {"success": True, "message": "Applied for gig successfully."},
            status=status.HTTP_201_CREATED,
        )


class PaymentAPIView(APIView):
    permission_classes = [AuthenticateOnlyArtist]
    serializer = PaymentSerializer

    def post(self, request, *args, **kwargs):
        serialized_data = self.serializer(data=request.data)
        if serialized_data.is_valid(raise_exception=True):
            # validate the gig
            if not Gig.objects.filter(
                id=serialized_data.validated_data["gig"].id,
                datetime__gte=timezone.localtime(timezone.now()),
                applications__user=request.user.artist_profile,
            ).exists():
                return Response(
                    {
                        "success": False,
                        "message": "Invalid Gig",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # check if this payment exists
            if Payment.objects.filter(
                gig=serialized_data.validated_data["gig"].id,
                user=request.user.artist_profile,
            ).exists():
                return Response(
                    {
                        "success": False,
                        "message": "Payment already exists for this gig.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serialized_data.save(user=request.user.artist_profile)
            return Response(
                {"success": True, "message": "Payment request sent!"},
                status=status.HTTP_201_CREATED,
            )

    def get(self, request, *args, **kwargs):
        if request.GET.get("action") == "get-gigs":
            gig_id = (
                Gig.objects.filter(
                    applications__user=request.user.artist_profile,
                    payment_gig__isnull=True,
                )
                .distinct()
                .values("id", "title")
            )
            return Response(
                {"success": True, "gigs": gig_id},
                status=status.HTTP_200_OK,
            )

        payment_instances = Payment.objects.filter(user=request.user.artist_profile)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(payment_instances, request)
        serializer = self.serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DocumentsAPIView(APIView):
    permission_classes = [AuthenticateOnlyArtist]
    serializer = DocumentsSerializer

    def get(self, request, *args, **kwargs):
        serilizer = self.serializer(
            request.user.artist_profile.singer_musician_info.documents
        )
        return Response(
            {"success": True, "documents": serilizer.data}, status=status.HTTP_200_OK
        )
