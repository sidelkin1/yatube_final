import logging
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост для проверки',
        )
        cls.public_pages = [
            '/',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.author.username}/',
            f'/posts/{cls.post.pk}/',
        ]
        cls.author_pages = [
            '/create/',
            f'/posts/{cls.post.pk}/edit/',
            f'/posts/{cls.post.pk}/delete/',
        ]
        cls.redirect_anon_pages = [
            '/create/',
            f'/posts/{cls.post.pk}/edit/',
            f'/posts/{cls.post.pk}/delete/',
            f'/posts/{cls.post.pk}/comment/',
            f'/profile/{cls.author.username}/follow/',
            f'/profile/{cls.author.username}/unfollow/',
        ]
        cls.redirect_notauthor_pages = [
            f'/posts/{cls.post.pk}/edit/',
            f'/posts/{cls.post.pk}/delete/',
        ]
        cls.urls_templates = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
            f'/posts/{cls.post.pk}/delete/':
                'posts/post_confirm_delete.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        # Убираем лишние сообщения
        cls.logger = logging.getLogger('django.request')
        cls.previous_level = cls.logger.getEffectiveLevel()
        cls.logger.setLevel(logging.ERROR)

    @classmethod
    def tearDownClass(cls):
        cls.logger.setLevel(cls.previous_level)
        super().tearDownClass()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент-автор
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.author)
        # Создаем авторизованый клиент-не-автор
        user = User.objects.create_user(username='not-author')
        self.authorized_client_na = Client()
        self.authorized_client_na.force_login(user)

    def test_public_url_exists_at_desired_location(self):
        """Страницы доступны любому пользователю."""
        for page in PostURLTests.public_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisiting_page(self):
        """Запрос к несуществующей странице вернёт ошибку 404."""
        response = self.guest_client.get('/unexisiting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_url_exists_at_desired_location(self):
        """Страницы доступны авторизованного пользователю-автору."""
        for page in PostURLTests.author_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymous_on_admin_login(self):
        """Страницы перенаправит анонимного пользователя
        на страницу логина.
        """
        for page in PostURLTests.redirect_anon_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={page}')

    def test_redirect_not_author_on_post_detail(self):
        """Страницы перенаправит пользователя-не-автора
        на страницу деталей поста.
        """
        for page in PostURLTests.redirect_notauthor_pages:
            with self.subTest(page=page):
                response = self.authorized_client_na.get(page, follow=True)
                self.assertRedirects(
                    response, f'/posts/{PostURLTests.post.pk}/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in PostURLTests.urls_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
