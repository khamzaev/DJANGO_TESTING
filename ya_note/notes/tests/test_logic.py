from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING
from .common import (
    TestBaseClass, NOTES_SUCCESS_URL, NOTES_ADD_URL,
    LOGIN_URL, EDIT_SLUG_URL, DELETE_SLUG_URL
)


FORM_DATA = {
    'title': 'Form title',
    'text': 'Form text',
    'slug': 'form-slug'
}


class TestNoteFunctionality(TestBaseClass):

    def test_user_can_create_note(self):
        """Проверяет создание заметки авторизованным пользователем."""
        notes_count_before = Note.objects.count()

        response = self.auth_author.post(
            NOTES_ADD_URL,
            data=FORM_DATA
        )

        self.assertEqual(Note.objects.count(), notes_count_before + 1)

        self.assertRedirects(response, NOTES_SUCCESS_URL)

        new_note = Note.objects.filter(slug=FORM_DATA['slug']).first()
        self.assertIsNotNone(new_note)

        self.assertEqual(new_note.title, FORM_DATA['title'])
        self.assertEqual(new_note.text, FORM_DATA['text'])
        self.assertEqual(new_note.slug, FORM_DATA['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_not_auth_user_cant_create_note(self):
        """
        Проверяет, что неавторизованный пользователь
        не может создать заметку.
        """
        note_count = Note.objects.count()
        response = self.client.post(NOTES_ADD_URL, data=FORM_DATA)
        expected_url = f'{LOGIN_URL}?next={NOTES_ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), note_count)

    def test_slug_unique(self):
        """Проверяет уникальность слага при создании заметки."""
        self.auth_author.post(NOTES_ADD_URL, data=FORM_DATA)
        response = self.auth_author.post(
            NOTES_ADD_URL,
            data=FORM_DATA
        )
        form = response.context['form']
        warning = FORM_DATA['slug'] + WARNING
        self.assertIn(warning, form.errors['slug'])

    def test_fill_slug(self):
        """
        Проверяет генерацию слага,
        если он не указан в форме.
        """
        form_data_without_slug = {
            key: value for key,
            value in FORM_DATA.items() if key != 'slug'
        }
        response = self.auth_author.post(
            NOTES_ADD_URL,
            data=form_data_without_slug
        )
        self.assertRedirects(response, NOTES_SUCCESS_URL)

        expected_slug = slugify(form_data_without_slug['title'])
        new_note = Note.objects.filter(slug=expected_slug).first()
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Проверяет, что автор может редактировать свою заметку."""
        notes_count_before = Note.objects.count()

        self.auth_author.post(EDIT_SLUG_URL, data=FORM_DATA)

        updated_note = Note.objects.get(id=self.note.id)

        self.assertEqual(Note.objects.count(), notes_count_before)

        self.assertEqual(updated_note.title, FORM_DATA['title'])
        self.assertEqual(updated_note.text, FORM_DATA['text'])
        self.assertEqual(updated_note.slug, FORM_DATA['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_other_user_cant_edit_note(self):
        """
        Проверяет, что другой пользователь
        не может редактировать чужую заметку.
        """
        notes_count_before = Note.objects.count()
        response = self.auth_other_user.post(
            EDIT_SLUG_URL,
            FORM_DATA
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        updated_note = Note.objects.get(id=self.note.id)

        self.assertEqual(Note.objects.count(), notes_count_before)

        self.assertEqual(updated_note.title, self.note.title)
        self.assertEqual(updated_note.text, self.note.text)
        self.assertEqual(updated_note.slug, self.note.slug)
        self.assertEqual(updated_note.author, self.note.author)

    def test_author_can_delete_note(self):
        """Проверяет, что автор может удалить свою заметку."""
        notes_before = Note.objects.count()

        response = self.auth_author.post(DELETE_SLUG_URL)

        self.assertRedirects(response, NOTES_SUCCESS_URL)

        notes_after = Note.objects.count()
        self.assertEqual(notes_after, notes_before - 1)

        self.assertFalse(Note.objects.filter(slug=self.note.slug).exists())

    def test_other_user_cant_delete_note(self):
        """
        Проверяет, что другой пользователь
        не может удалить чужую заметку.
        """
        notes_before = Note.objects.count()

        response = self.auth_other_user.post(DELETE_SLUG_URL)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.assertEqual(Note.objects.count(), notes_before)

        updated_note = Note.objects.get(id=self.note.id)

        self.assertEqual(updated_note.title, self.note.title)
        self.assertEqual(updated_note.text, self.note.text)
        self.assertEqual(updated_note.slug, self.note.slug)
        self.assertEqual(updated_note.author, self.note.author)
