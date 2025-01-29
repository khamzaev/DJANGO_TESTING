from http import HTTPStatus

from .common import (
    NOTES_HOME_URL, NOTES_LIST_URL,
    LOGIN_URL, NOTES_ADD_URL,
    NOTES_SUCCESS_URL, DETAIL_SLUG_URL,
    EDIT_SLUG_URL, DELETE_SLUG_URL,
    TestBaseClass, REDIRECT_URL
)


class NoteAccessTest(TestBaseClass):
    """Тесты для доступа к страницам заметок и страницам авторизации."""
    def test_access_to_pages(self):
        """
        Проверка доступа к страницам для анонимных и
        аутентифицированных пользователей.
        """
        parametrized_options = (
            (NOTES_HOME_URL, self.client, HTTPStatus.OK),
            (NOTES_LIST_URL, self.auth_author, HTTPStatus.OK),
            (NOTES_ADD_URL, self.auth_author, HTTPStatus.OK),
            (NOTES_SUCCESS_URL, self.auth_author, HTTPStatus.OK),
            (DETAIL_SLUG_URL, self.auth_author, HTTPStatus.OK),
            (EDIT_SLUG_URL, self.auth_author, HTTPStatus.OK),
            (DELETE_SLUG_URL, self.auth_author, HTTPStatus.OK),
            (DETAIL_SLUG_URL, self.auth_other_user, HTTPStatus.NOT_FOUND),
            (EDIT_SLUG_URL, self.auth_other_user, HTTPStatus.NOT_FOUND),
            (DELETE_SLUG_URL, self.auth_other_user, HTTPStatus.NOT_FOUND),
            (NOTES_LIST_URL, self.client, HTTPStatus.FOUND),
            (NOTES_ADD_URL, self.client, HTTPStatus.FOUND),
            (NOTES_SUCCESS_URL, self.client, HTTPStatus.FOUND),
            (DETAIL_SLUG_URL, self.client, HTTPStatus.FOUND),
            (EDIT_SLUG_URL, self.client, HTTPStatus.FOUND),
            (DELETE_SLUG_URL, self.client, HTTPStatus.FOUND),
        )
        for url, user, status in parametrized_options:
            with self.subTest(url=url, user=user, status=status):
                response = user.get(url)
                if status == HTTPStatus.FOUND:
                    self.assertRedirects(response, f'{LOGIN_URL}?next={url}')
                else:
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверяет редирект анонимных пользователей на страницу входа."""
        parametrized_options = (
            (EDIT_SLUG_URL, self.client),
            (DELETE_SLUG_URL, self.client),
            (DETAIL_SLUG_URL, self.client),
            (NOTES_LIST_URL, self.client),
            (NOTES_ADD_URL, self.client),
            (NOTES_SUCCESS_URL, self.client)
        )
        for url, user in parametrized_options:
            with self.subTest(url=url, user=user):
                self.assertRedirects(user.get(url), REDIRECT_URL + url)
