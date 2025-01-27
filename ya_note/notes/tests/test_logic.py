from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteFunctionality(TestCase):
    ADD_NOTE_URL = reverse('notes:add')

    def setUp(self):
        """Настройка данных для тестов."""
        self.form_data = {'title': 'Form title',
                          'text': 'Form text',
                          'slug': 'form-slug'}

        self.user = User.objects.create(username='Test User')
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

        self.author = User.objects.create(username='Test')
        self.author_client = Client()
        self.author_client.force_login(self.author)

        self.reader = User.objects.create(username='Simple')
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

        self.note = Note.objects.create(
            title='title',
            text='note text',
            slug='noteslug',
            author=self.author,
        )
        self.edit_note_url = reverse(
            'notes:edit',
            args=[self.note.slug])
        self.delete_note_url = reverse(
            'notes:delete',
            args=[self.note.slug])
        self.edit_form_data = {
            'title': 'new note title',
            'text': 'new note text'
        }

    def test_user_can_create_note(self):
        """Проверяет создание заметки авторизованным пользователем."""
        response = self.auth_client.post(
            self.ADD_NOTE_URL,
            data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))

        new_note = Note.objects.filter(slug=self.form_data['slug']).first()
        self.assertIsNotNone(new_note)

    def test_not_auth_user_cant_create_note(self):
        """
        Проверяет, что неавторизованный пользователь
        не может создать заметку.
        """
        response = self.client.post(self.ADD_NOTE_URL, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.ADD_NOTE_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_unique(self):
        """Проверяет уникальность слага при создании заметки."""
        self.auth_client.post(self.ADD_NOTE_URL, data=self.form_data)
        response = self.auth_client.post(
            self.ADD_NOTE_URL,
            data=self.form_data
        )
        form = response.context['form']
        warning = self.form_data['slug'] + WARNING
        self.assertIn(warning, form.errors['slug'])

    def test_fill_slug(self):
        """
        Проверяет генерацию слага,
        если он не указан в форме.
        """
        del self.form_data['slug']
        response = self.auth_client.post(
            self.ADD_NOTE_URL,
            data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))

        expected_slug = slugify(self.form_data['title'])
        new_note = Note.objects.filter(slug=expected_slug).first()
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Проверяет, что автор может редактировать свою заметку."""
        self.author_client.post(self.edit_note_url, self.edit_form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'new note title')

    def test_other_user_cant_edit_note(self):
        """
        Проверяет, что другой пользователь
        не может редактировать чужую заметку.
        """
        response = self.reader_client.post(
            self.edit_note_url,
            self.edit_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_can_delete_note(self):
        """Проверяет, что автор может удалить свою заметку."""
        response = self.author_client.post(self.delete_note_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """
        Проверяет, что другой пользователь
        не может удалить чужую заметку.
        """
        response = self.reader_client.post(self.delete_note_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
