from django.forms import ModelForm

from .models import Album


class AlbumForm(ModelForm):
    class Meta:
        model = Album
        fields = [
            'melon_id',
            'title',
            'img_cover',
            'release_date',
        ]
