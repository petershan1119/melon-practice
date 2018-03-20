from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from ..views import (
    index,
)

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('artist/', include('artist.urls.views')),
    path('album/', include('album.urls')),
    path('song/', include('song.urls')),

    path('', include('members.urls.views')),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)