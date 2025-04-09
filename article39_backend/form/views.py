from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Artist, FilmMaker
from .serializers import ArtistSerializer, FilmMakerSerializer
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from django.conf import settings


class ArtistView(APIView):

    def get(self, request, *args, **kwargs):
        artist_id = request.GET.get("id", None)

        if artist_id:
            # Retrieve a single artist by ID
            try:
                artist = Artist.objects.get(id=artist_id)
                serializer = ArtistSerializer(artist)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Artist.DoesNotExist:
                return Response(
                    {"success": False, "message": "Artist not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            # Retrieve all artists
            artists = Artist.objects.all().order_by("-created_at")
            serializer = ArtistSerializer(artists, many=True)
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
            )

    def post(self, request):
        serializer = ArtistSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"success": True, **serializer.data}, status=status.HTTP_201_CREATED
            )


class FilmMakerView(APIView):
    def post(self, request):
        serializer = FilmMakerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"success": True, "data":serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    def get(self, request, *args, **kwargs):
        film_maker_id = request.GET.get("id", None)
        if film_maker_id:
            try:
                film_maker = FilmMaker.objects.get(id=film_maker_id)
                serializer = FilmMakerSerializer(film_maker)
                return Response(serializer.data, status=status.HTTP_200_OK) 
            except FilmMaker.DoesNotExist:
                return Response(
                    {"success": False, "message": "FilmMaker not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            film_makers = FilmMaker.objects.all().order_by("-created_at")
            serializer = FilmMakerSerializer(film_makers, many=True)
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
            )


class UploadFile(APIView):
    # Upload raw file via cloudinary
    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"success": False, "message": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )

        upload_result = cloudinary.uploader.upload(file, folder="article39-files", resource_type="raw")
        return Response(
            {"success": True, "file_url": upload_result["secure_url"]},
            status=status.HTTP_201_CREATED,
        )
