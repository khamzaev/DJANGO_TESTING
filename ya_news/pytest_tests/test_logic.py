import pytest
from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from ya_news.news.models import Comment, News
from ya_news.news.forms import BAD_WORDS, WARNING
from django.test import Client

User = get_user_model()


@pytest.fixture
def news(db):
    """Фикстура для создания объекта новости."""
    return News.objects.create(
        title='Заголовок',
        text='Текст новости'
    )


@pytest.fixture
def user():
    return User.objects.create(
        username='Мимо Крокодил'
    )


@pytest.fixture
def auth_client():
    """Фикстура для авторизованного клиента."""
    user = User.objects.create(username='TestUser')
    client = Client()
    client.force_login(user)
    return client, user


@pytest.fixture
def form_data():
    return {'text': 'Текст комментария'}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(auth_client, news, form_data):
    client, user = auth_client
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{url}#comments'

    assert Comment.objects.count() == 1
    comment = Comment.objects.get()

    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == user


@pytest.mark.django_db
def test_user_cant_use_bad_words(auth_client, news):
    client, user = auth_client
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = client.post(url, data=bad_words_data)

    assert 'text' in response.context['form'].errors
    assert response.context['form'].errors['text'] == [WARNING]

    assert Comment.objects.count() == 0


@pytest.fixture
def author():
    return User.objects.create(
        username='Автор комментария'
    )


@pytest.fixture
def reader():
    return User.objects.create(
        username='Читатель'
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith('#comments')
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.delete(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    new_text = {'text': 'Обновлённый комментарий'}
    response = author_client.post(url, data=new_text)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith('#comments')

    comment.refresh_from_db()
    assert comment.text == new_text['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(reader_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    new_text = {'text': 'Обновлённый комментарий'}
    response = reader_client.post(url, data=new_text)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
