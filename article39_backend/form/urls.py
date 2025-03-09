from django.urls import path
from form.views import ArtistView, UploadFile

urlpatterns = [    
    path('artist/', ArtistView.as_view(), name='artists'),
    path('upload-file/', UploadFile.as_view(), name='upload-file'),

]
