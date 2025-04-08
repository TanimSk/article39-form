from django.urls import path
from artist.views import EnlistSongAPIView

urlpatterns = [
    path("song/", EnlistSongAPIView.as_view(), name="enlist-song"),
]
