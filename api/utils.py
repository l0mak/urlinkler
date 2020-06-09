import time
import re
from typing import List

from django.core.validators import URLValidator
from django.core.validators import ValidationError
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status

import redis


def redis_connection_init() -> redis.Redis:
    """
    Создание инстанса Redis
    :return: Redis Instance
    """
    redis_connection = redis.StrictRedis(host=settings.REDIS_HOST,
                                        port=settings.REDIS_PORT,
                                        db=0)
    return redis_connection


def post_visited_links(links: List[str]) -> Response:
    """
    Валидация и сохранение в базу массива ссылок с POST ручки

    :param links: list[str]
    :return: Response
    """
    timestamp = int(time.time())



    validate = URLValidator(schemes=('http', 'https'))

    for link in links:
        if not isinstance(link, str):
            response = {'status': f'{link} is not string'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # no protocol in URL case
        if '://' not in link:
            link = f'http://{link}'

        try:
            validate(link)
        except ValidationError:
            response = {'status': f'{link} failed url validation'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    for link in links:
        redis_connection_init().zadd('links', {link: timestamp})

    response = {'status': 'ok'}
    return Response(response, status=status.HTTP_201_CREATED)



def get_visited_domains(time_from: int, time_to: int) -> Response:
    """
    Запрос в инстанс Redis массива ссылок в диапозоне time_from time_to

    :param time_from: int time from epoch
    :param time_to: int time from epoch
    :return: Response
    """
    link_list = redis_connection_init().zrangebyscore('links', time_from, time_to)

    if not link_list:
        response = {'status': 'no data for request time range'}
        return Response(response, status=status.HTTP_204_NO_CONTENT)

    only_domains_set = set()

    for link in link_list:
        pattern = (r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+'
                    r'[a-z0-9][a-z0-9-]{0,61}[a-z0-9]')

        search = re.search(pattern, link.decode('utf-8'))
        only_domains_set.add(search.group(0))

    response = {
            'domains': only_domains_set,
            'status': 'ok',
            }

    return Response(response, status=status.HTTP_200_OK)