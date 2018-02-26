from django.forms import ModelForm

from .models import Artist


class ArtistForm(ModelForm):
    class Meta:
        model = Artist
        fields = [
            'melon_id',
            'name',
            'real_name',
            'nationality',
            'birth_date',
            'constellation',
            'blood_type',
            'intro',
        ]