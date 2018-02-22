from django.urls import path

from . import views

app_name = 'song'

urlpatterns = [
    path('', views.song_list, name='song-list'),
    path('search/', views.song_search, name='song-search'),
    path('search/melon/', views.song_search_from_melon, name='song-search-from-melon'),
    path('search/melon/add/', views.song_add_from_melon, name='song-add-from-melon'),
]