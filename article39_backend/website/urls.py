from django.urls import path
from website.views import CouraselImagesView, StoriesView, EventsView, TicketBookingsView, ExhibitionsView, AlbumView, SinglesView, ShowsView, ShowBookingInformationView

urlpatterns = [    
    path('courasel-images/', CouraselImagesView.as_view(), name='courasel-images'),
    path('stories/', StoriesView.as_view(), name='stories'),
    path('events/', EventsView.as_view(), name='events'),
    path('tickets/', TicketBookingsView.as_view(), name='tickets'),
    path('exhibitions/', ExhibitionsView.as_view(), name='exhibitions'),
    path('albums/', AlbumView.as_view(), name='albums'),
    path('singles/', SinglesView.as_view(), name='singles'),
    path('shows/', ShowsView.as_view(), name='shows'),
    path('bookings/', ShowBookingInformationView.as_view(), name='show-booking-information'),
]