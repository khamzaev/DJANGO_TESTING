from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args, user, expected_status',
    (
        ('news:home', None, None, HTTPStatus.OK),
        ('news:detail', None, None, HTTPStatus.OK),
        ('users:login', None, None, HTTPStatus.OK),
        ('users:logout', None, None, HTTPStatus.OK),
        ('users:signup', None, None, HTTPStatus.OK),
        ('news:edit', ('comment.id',), 'author', HTTPStatus.OK),
        ('news:edit', ('comment.id',), 'reader', HTTPStatus.NOT_FOUND),
        ('news:delete', ('comment.id',), 'author', HTTPStatus.OK),
        ('news:delete', ('comment.id',), 'reader', HTTPStatus.NOT_FOUND),
    )
)
def test_pages_availability(
        client, name, args, user, expected_status,
        author, reader, comment
):
    if user == 'author':
        client.force_login(author)
    elif user == 'reader':
        client.force_login(reader)

    if name == 'news:detail':
        args = (comment.id,)

    url = reverse(name, args=args)

    if name == 'users:logout':
        response = client.post(url)
    else:
        response = client.get(url)

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', 'comment.id'),
        ('news:delete', 'comment.id'),
    )
)
def test_redirect_for_anonymous_client(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=(args,))
    redirect_url = f'{login_url}?next={url}'

    response = client.get(url)
    assertRedirects(response, redirect_url)
