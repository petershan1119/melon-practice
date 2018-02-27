from django.urls import path

from . import views

app_name = 'song'

urlpatterns = [
    path('', views.song_list, name='song-list'),
    # path('search/', views.song_search, name='song-search'),
    path('add/', views.song_add, name='song-add'),
    path('<int:song_pk>/edit/', views.song_edit, name='song-edit'),
    path('<int:song_pk>/like-toggle/', views.song_like_toggle, name='song-like-toggle'),
    path('search/melon/', views.song_search_from_melon, name='song-search-from-melon'),
    path('search/melon/add/', views.song_add_from_melon, name='song-add-from-melon'),
    path('<int:song_pk>/', views.song_detail, name='song-detail'),
]