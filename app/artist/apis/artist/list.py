import json

from django.http import JsonResponse, HttpResponse

from ...models import Artist


__all__ = (
    'artist_list',
)


def artist_list(request):
    # localhost:8000/api/artist/
    artists = Artist.objects.all()
    # data = {
    #     'artists': artists,
    # }
    # return JsonResponse(data)
    # data = {
    #     'artists':
    # }
    data = {
        'artists': [{'melon_id': artist.melon_id,
                     'name': artist.name,
                     'real_name': artist.real_name,
                     'nationality': artist.nationality} for artist in artists],
    }
    # return HttpResponse(json.dumps(data), content_type='application/json')
    return JsonResponse(data)