from django.forms import ModelForm

from .models import Song


class SongForm(ModelForm):
    class Meta:
        model = Song
        fields = [
            'album',
            'song_id',
            'artists',
            'img_cover',
            'title',
            'genre',
            'lyrics',
        ]