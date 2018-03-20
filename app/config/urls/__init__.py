from django.urls import path, include

urlpatterns = [
    path('', include('config.urls.views')),
    path('apis/', include('config.urls.apis')),
]