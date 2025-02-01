from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Текст комментария'}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, news_detail):
    """
    Проверяет, что анонимный пользователь
    не может создать комментарий.
    """
    initial_comment_count = Comment.objects.count()

    client.post(news_detail, data=FORM_DATA)

    assert Comment.objects.count() == initial_comment_count


@pytest.mark.django_db
def test_user_can_create_comment(auth_client, news, user, news_detail):
    """
    Проверяет, что авторизованный пользователь
    может создать комментарий.
    """
    comments_before = set(Comment.objects.values_list('id', flat=True))

    response = auth_client.post(news_detail, data=FORM_DATA)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{news_detail}#comments'

    comments_after = set(Comment.objects.values_list('id', flat=True))

    new_comments = comments_after - comments_before

    assert len(new_comments) == 1

    new_comment = Comment.objects.get(id=new_comments.pop())

    assert new_comment.news == news
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == user


@pytest.mark.django_db
def test_user_cant_use_bad_words(auth_client, news, news_detail):
    """
    Проверяет, что нельзя использовать
    запрещённые слова в комментарии.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_count_before = Comment.objects.filter(news=news).count()
    response = auth_client.post(news_detail, data=bad_words_data)

    assert 'text' in response.context['form'].errors
    assert response.context['form'].errors['text'] == [WARNING]

    assert Comment.objects.filter(news=news).count() == comments_count_before

    assert not Comment.objects.filter(
        news=news,
        text=bad_words_data['text']).exists()


@pytest.mark.django_db
def test_author_can_delete_comment(
        author_client, comment, comment_delete, news_detail
):
    """Проверяет, что автор комментария может его удалить."""
    comments_before = Comment.objects.count()
    response = author_client.delete(comment_delete)

    assert response.status_code == HTTPStatus.FOUND
    expected_redirect_url = news_detail + '#comments'
    assert response.url == expected_redirect_url
    assert not Comment.objects.filter(id=comment.id).exists()

    comments_after = Comment.objects.count()
    assert comments_before - 1 == comments_after


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
        reader_client, comment, comment_delete
):
    """
    Проверяет, что пользователь не может
    удалить чужой комментарий.
    """
    comment_count_before = Comment.objects.count()
    comment_before = Comment.objects.get(id=comment.id)

    response = reader_client.delete(comment_delete)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comment_count_before

    comment_after = Comment.objects.get(id=comment.id)
    assert comment_after.id == comment_before.id
    assert comment_after.text == comment_before.text
    assert comment_after.author == comment_before.author
    assert comment_after.news == comment_before.news
    assert comment_after.created == comment_before.created


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, comment_edit):
    """
    Проверяет, что автор комментария может
    его отредактировать.
    """
    new_text = {'text': 'Обновлённый комментарий'}

    comments_count_before = Comment.objects.count()

    response = author_client.post(comment_edit, data=new_text)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url.endswith('#comments')

    updated_comment = Comment.objects.get(id=comment.id)

    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before

    assert updated_comment.text == new_text['text']
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author
    assert updated_comment.created == comment.created


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
        reader_client, comment, comment_edit
):
    """
    Проверяет, что пользователь не может
    редактировать чужой комментарий.
    """
    new_text = {'text': 'Обновлённый комментарий'}

    comments_count_before = Comment.objects.count()

    response = reader_client.post(comment_edit, data=new_text)

    assert response.status_code == HTTPStatus.NOT_FOUND

    updated_comment = Comment.objects.get(id=comment.id)

    assert updated_comment.text == comment.text
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author
    assert updated_comment.created == comment.created

    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before
