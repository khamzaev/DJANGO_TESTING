from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment

User = get_user_model()

# Пользователи
@pytest.fixture
def user():
    return User.objects.create(username='Мимо Крокодил')

@pytest.fixture
def author():
    return User.objects.create(username='Автор комментария')

@pytest.fixture
def reader():
    return User.objects.create(username='Читатель')

@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')

# Клиенты
@pytest.fixture
def auth_client(user):
    client = Client()
    client.force_login(user)
    return client

@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client

@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client

@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client

# Страницы
@pytest.fixture
def home_url():
    return reverse('news:home')

@pytest.fixture
def news_detail(news):
    return reverse('news:detail', args=[news.pk])

@pytest.fixture
def comment_edit(comment):
    return reverse('news:edit', args=[comment.pk])

@pytest.fixture
def comment_delete(comment):
    return reverse('news:delete', args=[comment.pk])

# Новости
@pytest.fixture
def news(db):
    """Создание единственной новости."""
    return News.objects.create(
        title='Заголовок',
        text='Текст новости'
    )

@pytest.fixture
def create_news():
    """Создание нескольких новостей."""
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

# Комментарии
@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )

@pytest.fixture
def create_comments(news, author):
    """Создание нескольких комментариев для новости."""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()

# Логин и редиректы
@pytest.fixture
def login():
    return reverse('users:login')

@pytest.fixture
def logout():
    return reverse('users:logout')

@pytest.fixture
def signup():
    return reverse('users:signup')

@pytest.fixture
def redirect_url_edit_comment(comment, login):
    return f'{login}?next={reverse("news:edit", args=[comment.pk])}'

@pytest.fixture
def redirect_url_delete_comment(comment, login):
    return f'{login}?next={reverse("news:delete", args=[comment.pk])}'
