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


# Страницы
@pytest.fixture
def home_url():
    return reverse('news:home')


# Новости
@pytest.fixture
def news(db):
    """Создание единственной новости."""
    return News.objects.create(
        title='Заголовок',
        text='Текст новости'
    )


@pytest.fixture
def login():
    return reverse('users:login')


@pytest.fixture
def login_redirect(login, comment, request):
    """
    Генерирует URL для редиректа с параметром next.
    Использует имя маршрута из параметризации теста.
    """
    route_name = request.param
    return f'{login}?next={reverse(route_name, args=(comment.id,))}'


@pytest.fixture
def detail_url(news):
    """Возвращает URL для страницы детали конкретной новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def delete_url(comment):
    """Возвращает URL для удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def edit_url(comment):
    """Возвращает URL для редактирования комментария."""
    return reverse('news:edit', kwargs={'pk': comment.id})


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
