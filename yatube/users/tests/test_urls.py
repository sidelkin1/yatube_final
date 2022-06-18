from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UserURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.public_pages = [
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/reset/done/',
        ]
        cls.private_pages = [
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_change/',
            '/auth/password_change/done/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
        ]
        cls.redirect_pages = [
            '/auth/password_change/',
            '/auth/password_change/done/',
        ]
        cls.urls_templates = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент-автор
        self.authorized_client = Client()
        self.authorized_client.force_login(UserURLTests.user)

    def test_public_url_exists_at_desired_location(self):
        """Страницы доступны неавторизованному пользователю."""
        for page in UserURLTests.public_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_url_exists_at_desired_location(self):
        """Страницы доступны авторизованному пользователю."""
        for page in UserURLTests.private_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymous_on_admin_login(self):
        """Страницы перенаправит анонимного пользователя
        на страницу логина.
        """
        for page in UserURLTests.redirect_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={page}')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in UserURLTests.urls_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
