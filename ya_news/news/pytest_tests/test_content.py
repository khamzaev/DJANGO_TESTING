import pytest
from datetime import datetime, timedelta
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.test import Client
from django.contrib.auth import get_user_model

from ya_news.news.forms import CommentForm
from ya_news.news.models import Comment, News

User = get_user_model()


@pytest.fixture
def create_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(min(settings.NEWS_COUNT_ON_HOME_PAGE, 10))
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def create_comments(create_news):

    author = User.objects.create_user(
        username='Комментатор',
        password='password'
    )

    news = News.objects.first()
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return news


@pytest.fixture
def client_with_author(create_comments):
    author = User.objects.get(username='Комментатор')
    client = Client()
    client.force_login(author)
    return client


@pytest.mark.django_db
def test_news_count(client, create_news):
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, create_news):
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, create_comments):
    detail_url = reverse(
        'news:detail',
        args=(create_comments.id,)
    )
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, create_comments):
    detail_url = reverse(
        'news:detail',
        args=(create_comments.id,)
    )
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client_with_author, create_comments):
    detail_url = reverse(
        'news:detail',
        args=(create_comments.id,)
    )
    response = client_with_author.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
