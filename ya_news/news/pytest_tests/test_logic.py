import pytest
from http import HTTPStatus
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_DATA = {'text': 'Текст комментария'}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=FORM_DATA)

    assert not Comment.objects.filter(
        news=news,
        text=FORM_DATA['text']).exists()


@pytest.mark.django_db
def test_user_can_create_comment(auth_client, news):
    client, user = auth_client
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=FORM_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{url}#comments'

    comment = Comment.objects.filter(
        news=news,
        text=FORM_DATA['text']).first()
    assert comment is not None
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

    assert not Comment.objects.filter(
        news=news,
        text=bad_words_data['text']).exists()


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)

    assert response.status_code == HTTPStatus.FOUND
    expected_redirect_url = reverse('news:detail', args=(comment.news.id,))
    assert response.url == expected_redirect_url
    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.delete(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    new_text = {'text': 'Обновлённый комментарий'}
    response = author_client.post(url, data=new_text)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith('#comments')

    updated_comment = Comment.objects.get(id=comment.id)

    assert Comment.objects.count() == 1
    assert updated_comment.text == new_text['text']
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author
    assert updated_comment.created == comment.created
    assert updated_comment.modified != comment.modified


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(reader_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    new_text = {'text': 'Обновлённый комментарий'}
    response = reader_client.post(url, data=new_text)

    assert response.status_code == HTTPStatus.NOT_FOUND

    updated_comment = Comment.objects.get(id=comment.id)

    assert updated_comment.text == comment.text
