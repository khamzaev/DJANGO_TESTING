import pytest

from news.forms import CommentForm
from yanews import settings


@pytest.mark.django_db
def test_news_count(client, create_news, home_url):
    """Проверяет количество новостей на главной странице."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, create_news, home_url):
    """Проверяет порядок новостей на главной странице по дате."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, create_comments, detail_url, news):
    """
    Проверяет порядок комментариев к новости по времени создания.
    """
    client.get(detail_url)

    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)

    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news, detail_url):
    """Проверяет отсутствие формы для анонимного пользователя."""
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(auth_client, news, detail_url):
    """Проверяет наличие формы для авторизованного пользователя."""
    response = auth_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
