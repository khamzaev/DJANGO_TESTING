from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from notes.models import Note
from .common import user, note


class TestHomePage(TestCase):
    """Тесты для домашней страницы."""

    HOME_URL = reverse('notes:home')

    def test_home_page(self):
        response = self.client.get(self.HOME_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/home.html')


class TestNotesList(TestCase):
    """Тесты для страницы списка заметок."""

    NOTES_LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.user = user()
        cls.notes = [
            Note.objects.create(
                title=f'Заметка {i}',
                text=f'Текст заметки {i}',
                author=cls.user
            )
            for i in range(5)
        ]

    def test_notes_list(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.NOTES_LIST_URL)
        notes_count = Note.objects.count()
        self.assertEqual(len(response.context['object_list']), notes_count)


class TestNoteCreate(TestCase):
    """Тесты для создания заметки."""

    CREATE_NOTE_URL = reverse('notes:add')

    def test_create_note_anonymous_user(self):
        response = self.client.get(self.CREATE_NOTE_URL)
        expected_url = f"{settings.LOGIN_URL}?next={self.CREATE_NOTE_URL}"
        self.assertRedirects(response, expected_url)

    def test_create_note_authenticated_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.CREATE_NOTE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/form.html')


class TestNoteUpdate(TestCase):
    """Тесты для редактирования заметки."""

    @classmethod
    def setUpTestData(cls):
        cls.user = user()
        cls.note = note(cls.user)
        cls.update_url = reverse('notes:edit', args=[cls.note.slug])

    def test_update_note_authenticated_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/form.html')

    def test_update_note_anonymous_user(self):
        response = self.client.get(self.update_url)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.update_url}'
        self.assertRedirects(response, expected_url)


class TestNoteDelete(TestCase):
    """Тесты для удаления заметки."""

    @classmethod
    def setUpTestData(cls):
        cls.user = user()
        cls.note = note(cls.user)
        cls.delete_url = reverse('notes:delete', args=[cls.note.slug])

    def test_delete_note_authenticated_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/delete.html')
