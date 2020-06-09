import pytest
import redis
import json

from django.conf import settings
from django.urls import reverse_lazy



def test_methods(client):
    """
    GET метод на POST ручку и наоборот
    :param client:
    :return:
    """
    post_url = reverse_lazy('visited_links')
    response = client.get(post_url)
    assert response.status_code == 405

    get_url = reverse_lazy('visited_domains')
    response = client.post(get_url)
    assert response.status_code == 405



def test_check_post_currupted(client):
    """
    POST невалидных данных
    :param client:
    :return:
    """
    post_url = reverse_lazy('visited_links')

    inputs = [
                None,
                {},
                b'{likn: [[}',
            ]

    for _ in inputs:
        response = client.post(post_url, _,
                               content_type='application/json')
        assert response.status_code == 400



def test_post_no_links(client):
    """
    POST с пустым массивом ссылок
    :param client:
    :return:
    """
    post_url = reverse_lazy('visited_links')

    json_input = {'links': []}
    json_output = {'status': 'no links in request data'}

    response = client.post(post_url, json_input,
                           content_type='application/json')
    assert response.status_code == 400
    assert response.json() == json_output



@pytest.fixture
def create_test_redis(request):
    """
    Создание отдельного тестового инстанса REDIS
    :param request:
    :return:
    """
    redis_connection = redis.StrictRedis(host=settings.REDIS_HOST,
                                        port=settings.REDIS_PORT,
                                        db=1)

    request.addfinalizer(redis_connection.flushall)
    return redis_connection


@pytest.fixture
def create_test_links(create_test_redis):
    """
    Сохранение ссылок в тестовом инстансе REDIS
    :param create_test_redis:
    :return:
    """
    links = [
        'https://ya.ru',
        'https://ya.ru?q=123',
        'funbox.ru',
        'https://stackoverflow.com/questions/11828270'
    ]
    timestamp = 1545221231
    for _ in links:
        create_test_redis.zadd('links', {_: timestamp})


def test_post_visited_links(client):
    """
    POST валидных данных
    :param client:
    :return:
    """
    url = reverse_lazy('visited_links')
    data = {
        'links': [
            'https://ya.ru',
            'https://ya.ru?q=123',
            'funbox.ru',
            'https://stackoverflow.com/questions/11828270/'
        ]
    }
    response = client.post(url, data=data, content_type='application/json')
    json_data = json.loads(response.content)
    assert json_data['status'] == 'ok'
    assert response.status_code == 201



def test_get_visited_domains(client):
    """
    GET запрос на ссылки из теста test_post_visited_links
    :param client:
    :return:
    """
    date_from = '1245221231'
    date_to = '1745217638'

    url = reverse_lazy('visited_domains')
    url_query_range = f'{url}?from={date_from}&to={date_to}'

    response = client.get(url_query_range)

    json_data = response.json()


    assert response.status_code == 200
    assert json_data['status'] == 'ok'

    for domain in json_data['domains']:
        assert domain in ['ya.ru', 'stackoverflow.com', 'funbox.ru']
