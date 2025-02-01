from http import HTTPStatus

import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args, user, expected_status, http_method',
    (
        ('news:home', None, pytest.lazy_fixture('author'),
         HTTPStatus.OK, 'get'),
        ('news:home', None, pytest.lazy_fixture('reader'),
         HTTPStatus.OK, 'get'),
        ('news:detail', pytest.lazy_fixture('news'),
         pytest.lazy_fixture('author'), HTTPStatus.OK, 'get'),
        ('news:detail', pytest.lazy_fixture('news'),
         pytest.lazy_fixture('reader'), HTTPStatus.OK, 'get'),
        ('users:login', None, pytest.lazy_fixture('author'),
         HTTPStatus.OK, 'get'),
        ('users:login', None, pytest.lazy_fixture('reader'),
         HTTPStatus.OK, 'get'),
        ('users:logout', None, pytest.lazy_fixture('author'),
         HTTPStatus.OK, 'post'),
        ('users:logout', None, pytest.lazy_fixture('reader'),
         HTTPStatus.OK, 'post'),
        ('users:signup', None, pytest.lazy_fixture('author'),
         HTTPStatus.OK, 'get'),
        ('users:signup', None, pytest.lazy_fixture('reader'),
         HTTPStatus.OK, 'get'),
    )
)
def test_pages_availability(
        client, name, args, user, expected_status, http_method
):
    """Проверка доступности страниц для разных пользователей."""
    method = getattr(client, http_method)

    url = reverse(name, args=getattr(args, 'id', []) and [args.id])
    response = method(url)

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, login_redirect',
    (
            ('news:edit', 'news:edit'),
            ('news:delete', 'news:delete'),
    ),
    indirect=['login_redirect']
)
def test_redirect_for_anonymous_client(
        client, name, login_redirect, comment
):
    """
    Проверяет редирект анонимного пользователя на страницы
    редактирования и удаления комментариев.
    """
    url = reverse(name, args=(comment.id,))
    response = client.get(url)

    assertRedirects(response, login_redirect)
