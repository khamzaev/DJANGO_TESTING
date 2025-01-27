from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

from notes.models import Note

User = get_user_model()


class TestNotesViews(TestCase):
    """Тесты для всех страниц заметок."""

    def setUp(self):
        """Создаём пользователя и тестовые заметки."""
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=self.user,
            slug='test-slug'
        )
        self.HOME_URL = reverse('notes:home')
        self.NOTES_LIST_URL = reverse('notes:list')
        self.CREATE_NOTE_URL = reverse('notes:add')
        self.UPDATE_NOTE_URL = reverse('notes:edit', args=[self.note.slug])
        self.DELETE_NOTE_URL = reverse('notes:delete', args=[self.note.slug])
        self.DETAIL_NOTE_URL = reverse('notes:detail', args=[self.note.slug])

    def test_home_page(self):
        """Проверяем доступность главной страницы и используемый шаблон."""
        response = self.client.get(self.HOME_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/home.html')

    def test_notes_list(self):
        """Сравниваем количество заметок в базе с количеством в контексте."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.NOTES_LIST_URL)
        db_notes_count = Note.objects.count()
        self.assertEqual(len(response.context['object_list']), db_notes_count)

    def test_create_note_anonymous_user(self):
        """
        Проверяем, что анонимный пользователь
        перенаправляется на страницу входа.
        """
        response = self.client.get(self.CREATE_NOTE_URL)
        expected_url = f"{settings.LOGIN_URL}?next={self.CREATE_NOTE_URL}"
        self.assertRedirects(response, expected_url)

    def test_create_note_authenticated_user(self):
        """
        Проверяем доступность страницы создания заметки
        для авторизованного пользователя.
        """
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.CREATE_NOTE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/form.html')

    def test_update_note_authenticated_user(self):
        """
        Проверяем доступность страницы для
        авторизованного пользователя.
        """
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.UPDATE_NOTE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/form.html')

    def test_update_note_anonymous_user(self):
        """
        Проверяем, что анонимный пользователь перенаправляется
        на страницу входа.
        """
        response = self.client.get(self.UPDATE_NOTE_URL)
        login_url = reverse('users:login')
        self.assertRedirects(
            response,
            f'{login_url}?next={self.UPDATE_NOTE_URL}'
        )

    def test_update_note_valid_form(self):
        """
        Проверяем, что авторизованный
        пользователь может обновить заметку.
        """
        self.client.login(username='testuser', password='password')
        data = {
            'title': 'Обновлённая заметка',
            'text': 'Обновлённый текст',
            'slug': 'updated-slug'
        }
        response = self.client.post(self.UPDATE_NOTE_URL, data)
        self.assertRedirects(response, reverse('notes:success'))
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, 'Обновлённая заметка')
        self.assertEqual(updated_note.text, 'Обновлённый текст')

    def test_delete_note_authenticated_user(self):
        """
        Проверяем доступность страницы для
        авторизованного пользователя.
        """
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.DELETE_NOTE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/delete.html')

    def test_delete_note_anonymous_user(self):
        """
        Проверяем, что анонимный пользователь
        перенаправляется на страницу входа.
        """
        response = self.client.get(self.DELETE_NOTE_URL)
        self.assertRedirects(
            response,
            f'/auth/login/?next={self.DELETE_NOTE_URL}'
        )

    def test_delete_note_valid_post(self):
        """Проверяем, что авторизованный пользователь может удалить заметку."""
        self.client.login(username='testuser', password='password')
        response = self.client.post(self.DELETE_NOTE_URL)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_note_detail(self):
        """Проверяем отображение страницы заметки для авторизованного пользователя."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.DETAIL_NOTE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/detail.html')
        self.assertIn('note', response.context)
        self.assertEqual(response.context['note'], self.note)
