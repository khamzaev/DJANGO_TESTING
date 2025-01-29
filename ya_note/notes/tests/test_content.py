from .common import (
    TestBaseClass, NOTES_HOME_URL, DETAIL_SLUG_URL,
    NOTES_ADD_URL, NOTES_LIST_URL
)
from notes.models import Note
from notes.forms import NoteForm


class TestNotesContent(TestBaseClass):
    """Тесты для проверки контента страниц заметок."""
    def setUp(self):
        super().setUp()

    def test_home_page(self):
        """
        Проверяем доступность главной страницы
        и используемый шаблон.
        """
        response = self.auth_author.get(NOTES_HOME_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/home.html')

    def test_notes_list(self):
        """
        Проверяем, сколько заметок отображается
        на главной странице.
        """
        response = self.auth_author.get(NOTES_LIST_URL)
        notes_count = Note.objects.count()
        self.assertEqual(
            response.context['object_list'].count(),
            notes_count
        )

    def test_create_note_authenticated_user(self):
        """
        Проверяем доступность страницы создания заметки и
        проверяем содержимое формы для авторизованного пользователя.
        """
        response = self.auth_author.get(NOTES_ADD_URL)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'notes/form.html')

        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="text"')
        self.assertContains(response, 'name="slug"')

    def test_note_detail(self):
        """
        Проверяем отображение страницы заметки
        для авторизованного пользователя.
        """
        response = self.auth_author.get(DETAIL_SLUG_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/detail.html')
        self.assertIn('note', response.context)
        self.assertEqual(response.context['note'], self.note)
