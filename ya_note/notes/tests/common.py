from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()
SLUG = 'podrobnosti'
NOTES_HOME_URL = reverse('notes:home')
NOTES_LIST_URL = reverse('notes:list')
NOTES_ADD_URL = reverse('notes:add')
NOTES_SUCCESS_URL = reverse('notes:success')
SIGN_UP_URL = reverse('users:signup')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
REDIRECT_URL = f'{LOGIN_URL}?next='
DETAIL_SLUG_URL = reverse('notes:detail', args=(SLUG,))
EDIT_SLUG_URL = reverse('notes:edit', args=(SLUG,))
DELETE_SLUG_URL = reverse('notes:delete', args=(SLUG,))


class TestBaseClass(TestCase):
    """Общий класс с фикстурами для всех тестов."""
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.other_user = User.objects.create(username='Reader')
        cls.auth_author, cls.auth_other_user = Client(), Client()
        cls.auth_author.force_login(cls.author)
        cls.auth_other_user.force_login(cls.other_user)
        cls.note = Note.objects.create(
            title='Название заметки',
            text='Подробности',
            slug=SLUG,
            author=cls.author
        )
        cls.note_previous_count = Note.objects.count()
