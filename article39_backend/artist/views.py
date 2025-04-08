from django.shortcuts import render
from rest_framework.views import APIView, Response, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination

# serializers
from artist.serializers import SongSerializer


# Pagination Config
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
    page_query_param = "p"


# Authenticate User Only Class
class AuthenticateOnlyArtist(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_artist:
                return True
            else:
                return False
        return False


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

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = SongSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
