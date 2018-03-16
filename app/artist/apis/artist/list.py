import json

from django.http import HttpResponse, JsonResponse

from artist.models import Artist

__all__ = (
    'artist_list',
)


def artist_list(request):
    """
    'data': {
        'artists': [
            {
                'melon_id': ...,
                'name': ...,
            },
            {
                'melon_id': ...,
                'name': ...,
            },
            ...
        ]
    }
    :param request:
    :return:
    """
    # localhost:8000/api/artist/
    artists = Artist.objects.all()
    data = {
        'artists': [artist.to_json() for artist in artists],
    }
    # return HttpResponse(
    #     json.dumps(data),
    #     content_type='application/json')
    return JsonResponse(data)

# /artist/       -> artist.urls.views
# /api/artist/   -> artist.urls.apis

# /album/        -> album.urls.views
# /api/album/    -> album.urls.apis