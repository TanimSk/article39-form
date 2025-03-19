from django.urls import path
from form.views import ArtistView, UploadFile, FilmMakerView

urlpatterns = [    
    path('artist/', ArtistView.as_view(), name='artists'),
    path('upload-file/', UploadFile.as_view(), name='upload-file'),
    path('filmmaker/', FilmMakerView.as_view(), name='filmmaker'),
]
