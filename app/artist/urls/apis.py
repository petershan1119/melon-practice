from django.urls import path

from .. import apis

app_name = 'artist'

urlpatterns = [
    path('', apis.artist_list, name='artist-list'),
    path('drf/', apis.ArtistListView.as_view(), name='artist-list-2'),
]