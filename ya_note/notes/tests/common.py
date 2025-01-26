import pytest
from django.contrib.auth import get_user_model
from notes.models import Note


User = get_user_model()


@pytest.fixture
def user():
    """Создаёт пользователя для использования в тестах."""
    return User.objects.create_user(
        username='testuser',
        password='password'
    )

@pytest.fixture
def note(user):
    """Создаёт заметку для использования в тестах."""
    return Note.objects.create(
        title='Тестовая заметка',
        text='Текст заметки',
        author=user,
        slug='test-slug'
    )
