from django.urls import path
from artist.views import EnlistSongAPIView, GigAPIView, PaymentAPIView

urlpatterns = [
    path("music-songs/", EnlistSongAPIView.as_view(), name="enlist-song"),
    path("gigs/", GigAPIView.as_view(), name="gigs"),
    path("payment/", PaymentAPIView.as_view(), name="payments"),
]
