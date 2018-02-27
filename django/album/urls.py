from django.urls import path
from . import views

app_name = 'album'
urlpatterns = [
    path('', views.album_list, name='album-list'),
    path('add/', views.album_add, name='album-add'),
    path('<int:album_pk>/edit/', views.album_edit, name='album-edit'),
    path('<int:album_pk>/', views.album_detail, name='album-detail'),
    path('<int:album_pk>/like-toggle/', views.album_like_toggle, name='album-like-toggle'),
    path('search/melon/', views.album_search_from_melon, name='album-search-from-melon'),
    path('search/melon/add', views.album_add_from_melon, name='album-add-from-melon'),
]