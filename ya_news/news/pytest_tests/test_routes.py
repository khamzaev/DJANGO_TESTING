from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability(client, name, args, news):
    """Проверка доступности страниц для анонимного пользователя."""
    if name == 'news:detail':
        args = (news.id,)
    url = reverse(name, args=args)
    if name == 'users:logout':
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user, expected_status',
    (
        ('author', HTTPStatus.OK),
        ('reader', HTTPStatus.NOT_FOUND),
    )
)
def test_availability_for_comment_edit_and_delete(
        client, user, expected_status, author, reader, comment
):
    """
    Проверяет доступность страниц редактирования и удаления
    комментариев для авторизованных пользователей.
    """
    user_instance = author if user == 'author' else reader
    client.force_login(user_instance)

    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        response = client.get(url)
        assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirect_for_anonymous_client(client, name, comment):
    """
    Проверяет редирект анонимного пользователя на страницы
    редактирования и удаления комментариев.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'

    response = client.get(url)
    assertRedirects(response, redirect_url)
