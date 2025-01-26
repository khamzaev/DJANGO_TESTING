import uuid

import pytest
from datetime import datetime, timedelta
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import Client

from news.models import News, Comment


User = get_user_model()


@pytest.fixture
def unique(request):
    """Фикстура для создания уникальных значений"""
    def _unique(prefix):
        return f"{prefix}_{uuid.uuid4().hex}"
    return _unique

@pytest.fixture
def create_user(unique):
    username = unique('username')
    return User.objects.create_user(
        username=username,
        password='password'
    )


@pytest.fixture
def client_with_author(create_user):
    client = Client()
    client.force_login(create_user)
    return client


@pytest.fixture
def home_url():
    return reverse('news:home')


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
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client
