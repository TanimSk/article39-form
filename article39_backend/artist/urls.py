from django.urls import path
from artist.views import (
    EnlistSongAPIView,
    GigAPIView,
    PaymentAPIView,
    DocumentsAPIView,
    DashboardAPIView,
)

urlpatterns = [
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),
    path("music-songs/", EnlistSongAPIView.as_view(), name="enlist-song"),
    path("gigs/", GigAPIView.as_view(), name="gigs"),    
    path("payment/", PaymentAPIView.as_view(), name="payments"),
    path("documents/", DocumentsAPIView.as_view(), name="documents"),
]
