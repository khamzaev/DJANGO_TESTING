from .common import (
    TestBaseClass, NOTES_ADD_URL,
    NOTES_LIST_URL, EDIT_SLUG_URL
)
from notes.forms import NoteForm


class TestNotesContent(TestBaseClass):
    """Тесты для проверки контента страниц заметок."""

    def test_notes_list_contains_only_user_notes(self):
        """
        Проверяем, что в списке отображаются
        только заметки текущего пользователя.
        """
        response = self.auth_author.get(NOTES_LIST_URL)
        notes = response.context['object_list']

        self.assertTrue(all(note.author == self.author for note in notes))

        self.assertIn(self.note, notes)

        response_other = self.auth_other_user.get(NOTES_LIST_URL)
        self.assertNotIn(self.note, response_other.context['object_list'])

    def test_create_note_page_contains_form(self):
        """
        Проверяем, что на странице
        создания заметки передаётся форма.
        """
        response = self.auth_author.get(NOTES_ADD_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/form.html')

        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_note_page_contains_form(self):
        """
        Проверяем, что на странице редактирования
        заметки передаётся форма.
        """
        response = self.auth_author.get(EDIT_SLUG_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/form.html')

        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
