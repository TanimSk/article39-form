from django.urls import path
from website.views import CouraselImagesView, StoriesView, EventsView, TicketBookingsView, ExhibitionsView

urlpatterns = [    
    path('courasel-images/', CouraselImagesView.as_view(), name='courasel-images'),
    path('stories/', StoriesView.as_view(), name='stories'),
    path('events/', EventsView.as_view(), name='events'),
    path('tickets/', TicketBookingsView.as_view(), name='tickets'),
    path('exhibitions/', ExhibitionsView.as_view(), name='exhibitions'),
]