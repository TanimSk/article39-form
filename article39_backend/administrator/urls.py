from django.urls import path
from administrator.views import GigAPIView, CreateArtistAccountAPIView, SongMusicAPIView

urlpatterns = [
    path("gig/", GigAPIView.as_view(), name="gig"),
    path("verify-artist/", CreateArtistAccountAPIView.as_view(), name="verify-artist"),
    path("music-songs/", SongMusicAPIView.as_view(), name="music-songs"),

]
