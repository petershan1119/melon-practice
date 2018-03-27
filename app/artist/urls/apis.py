from django.urls import path

from .. import apis

app_name = 'artist'

urlpatterns = [
    # path('', apis.artist_list, name='artist-list'),
    path('', apis.ArtistListCreateView.as_view(), name='artist-list'),
    path('<int:pk>/', apis.ArtistRetrieveUpdateDestroyView.as_view(), name='artist-detail'),
]