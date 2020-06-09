from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .utils import post_visited_links
from .utils import get_visited_domains



@api_view(['POST'])
def visited_links_handle(request):
    """
    POST ручка для приема массива ссылок:

    POST
    {
        "links": [
                "https://ya.ru",
                "https://ya.ru?q=123",
                "funbox.ru",
                "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
                ]
    }

    RESPONSE
    {
        "status": "ok"
    }
    """

    if not 'links' in request.data or not request.data['links']:
        response = {'status': 'no links in request data'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    else:
        links = request.data['links']
        return post_visited_links(links)



@api_view(['GET'])
def visited_domains_handle(request):
    """
    GET ручка для получения массива ссылок в диапозоне времени:

    GET /visited_domains?from=1545221231&to=1545217638

    RESPONSE
    {
        "domains": [
                    "ya.ru",
                    "funbox.ru",
                    "stackoverflow.com"
                    ],
        "status": "ok"
    }
    """
    time_from = request.GET.get('from')
    time_to = request.GET.get('to')

    if not time_from or not time_to:
        response = {'status': 'no time range in request'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    if not time_from.isdigit() or not time_to.isdigit():
        response = {'status': 'time range must be digits'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    if time_from > time_to:
        time_from, time_to = time_to, time_from

    return get_visited_domains(time_from, time_to)