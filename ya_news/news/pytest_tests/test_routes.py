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
    """
    Тестирование доступности различных страниц сайта.

    Этот тест проверяет доступность главных страниц сайта (новости, логин, регистрация, выход)
    для анонимного пользователя. Для страницы 'news:detail' в качестве аргумента передается
    ID новости. Ожидается, что для всех страниц статус ответа будет 200 (HTTPStatus.OK).
    """
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
    Тестирование доступности страницы редактирования и удаления комментария.

    Этот тест проверяет, может ли автор или читатель редактировать и удалять комментарии.
    Ожидается, что автор сможет получить доступ к этим страницам с кодом состояния 200,
    а читатель получит ошибку 404 (HTTPStatus.NOT_FOUND).
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
    Тестирование редиректа для анонимного пользователя на страницы редактирования и удаления комментариев.

    Этот тест проверяет, что анонимный пользователь, пытающийся попасть на страницу редактирования или удаления комментария,
    будет перенаправлен на страницу логина с параметром next, указывающим на запрашиваемую страницу.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'

    response = client.get(url)
    assertRedirects(response, redirect_url)
