from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author',
            password='password'
        )
        cls.reader = User.objects.create_user(
            username='reader',
            password='password'
        )

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст тестовой заметки',
            author=cls.author
        )

    def test_pages_availability_and_redirects(self):
        """
        Проверяет доступность страниц и
        редиректы для различных пользователей.
        """
        for name, args in (
                ('notes:home', None),
                ('notes:add', None),
                ('notes:edit', (self.note.slug,)),
                ('notes:detail', (self.note.slug,)),
                ('notes:delete', (self.note.slug,)),
                ('notes:list', None),
                ('notes:success', None),
        ):
            with self.subTest(name=name):
                self.client.force_login(self.author)
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

                self.client.logout()
                response = self.client.get(url)
                if name == 'notes:add':
                    login_url = reverse('users:login')
                    redirect_url = f'{login_url}?next={url}'
                    self.assertRedirects(response, redirect_url)
                elif name == 'notes:detail':
                    redirect_url = f'{reverse("users:login")}?next={url}'
                    self.assertRedirects(response, redirect_url)
                elif name == 'notes:list':
                    redirect_url = f'{reverse("users:login")}?next={url}'
                    self.assertRedirects(response, redirect_url)
                elif name in ('notes:edit', 'notes:delete'):
                    self.assertRedirects(
                        response,
                        reverse('users:login') + f'?next={url}'
                    )

        self.client.force_login(self.reader)
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        """
        Проверяет редирект для анонимного пользователя.
        На страницы редактирования и удаления.
        """
        login_url = reverse('users:login')

        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
