import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args, user, expected_status',
    (
        ('news:home', None, 'author', HTTPStatus.OK),
        ('news:home', None, 'reader', HTTPStatus.OK),
        ('news:detail', None, 'author', HTTPStatus.OK),
        ('news:detail', None, 'reader', HTTPStatus.OK),
        ('users:login', None, 'author', HTTPStatus.OK),
        ('users:login', None, 'reader', HTTPStatus.OK),
        ('users:logout', None, 'author', HTTPStatus.OK),
        ('users:logout', None, 'reader', HTTPStatus.OK),
        ('users:signup', None, 'author', HTTPStatus.OK),
        ('users:signup', None, 'reader', HTTPStatus.OK),
    )
)
def test_pages_availability(
        client, name, args, user,
        expected_status, author, reader, news
):
    """Проверка доступности страниц для разных пользователей."""
    user_instance = author if user == 'author' else reader
    client.force_login(user_instance)

    if name == 'news:detail':
        args = (news.id,)

    url = reverse(name, args=args)
    if name == 'users:logout':
        response = client.post(url)
    else:
        response = client.get(url)

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, user',
    (
        ('news:edit', 'author'),
        ('news:edit', 'reader'),
        ('news:delete', 'author'),
        ('news:delete', 'reader'),
    )
)
def test_redirect_for_anonymous_client(client, name, user, comment):
    """
    Проверяет редирект анонимного пользователя на страницы
    редактирования и удаления комментариев.
    """
    url = reverse(name, args=(comment.id,))
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={url}'

    response = client.get(url)

    assertRedirects(response, redirect_url)