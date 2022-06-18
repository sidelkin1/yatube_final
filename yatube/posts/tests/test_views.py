import logging
import unittest
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post

User = get_user_model()


class PostViewsTests(TestCase):

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
            group=cls.group,
        )
        cls.pages_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': cls.author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.pk}
            ): 'posts/create_post.html',
            reverse(
                'posts:post_delete',
                kwargs={'post_id': cls.post.pk}
            ): 'posts/post_confirm_delete.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        cls.post_list_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.author.username}),
        ]
        cls.create_edit_pages = [
            reverse('posts:post_edit', kwargs={'post_id': cls.post.pk}),
            reverse('posts:post_create'),
        ]
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
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTests.author)
        # Клиент для проверки CSRF
        self.csrf_client = Client(enforce_csrf_checks=True)

    def test_custom_404_template(self):
        """Тест кастомной страницы 404."""
        response = self.guest_client.get(None)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_custom_403csrf_template(self):
        """Тест кастомной страницы 403."""
        response = self.csrf_client.post(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'core/403csrf.html')

    def test_reverse_uses_correct_template(self):
        """reverse использует соответствующий шаблон."""
        for page, template in PostViewsTests.pages_templates.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(page)
                self.assertTemplateUsed(response, template)

    def test_posts_page_list_is_1(self):
        """На страницах со списком постов должно быть ровна 1 запись."""
        for page in PostViewsTests.post_list_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertIn('page_obj', response.context)
                page_obj = response.context['page_obj']
                self.assertIsInstance(page_obj, Page)
                self.assertEqual(page_obj.paginator.count, 1)

    def test_posts_page_show_correct_context(self):
        """Шаблоны со списком постов сформированы с правильным контекстом."""
        for page in PostViewsTests.post_list_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertIn('page_obj', response.context)
                page_obj = response.context['page_obj']
                self.assertIsInstance(page_obj, Page)
                self.assertIn(PostViewsTests.post, page_obj)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostViewsTests.post.pk})
        )
        self.assertIn('post', response.context)
        post = response.context['post']
        self.assertIsInstance(post, Post)
        self.assertEqual(post, PostViewsTests.post)

    def test_post_form_show_correct_context(self):
        """Шаблоны создания/редактирования постов сформированы
        с правильным контекстом."""
        for page in PostViewsTests.create_edit_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsInstance(form, PostForm)

    def test_creation_post_with_new_group(self):
        """Проверка корректного создания поста с новой группой."""
        new_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        new_post = Post.objects.create(
            author=PostViewsTests.author,
            text='Тестовый пост для проверки 2',
            group=new_group,
        )
        # Проверка списка постов без привязки к группе
        pages = [
            reverse('posts:index'),
            reverse('posts:profile',
                    kwargs={'username': new_post.author.username}),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertIn('page_obj', response.context)
                page_obj = response.context['page_obj']
                self.assertIsInstance(page_obj, Page)
                self.assertEqual(page_obj.paginator.count, 2)
        # Проверка списка постов с привязкой к группе
        for group in [new_group, PostViewsTests.group]:
            with self.subTest(group=group):
                response = self.guest_client.get(
                    reverse('posts:group_list',
                            kwargs={'slug': group.slug})
                )
                self.assertIn('page_obj', response.context)
                page_obj = response.context['page_obj']
                self.assertIsInstance(page_obj, Page)
                self.assertEqual(page_obj.paginator.count, 1)

    def test_add_comment(self):
        """Комментировать посты может только авторизованный пользователь."""
        page = reverse('posts:add_comment',
                       kwargs={'post_id': PostViewsTests.post.pk})
        response = self.guest_client.post(page, follow=True)
        self.assertRedirects(response, f'/auth/login/?next={page}')
        response = self.authorized_client.post(page, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @unittest.skip('Требуется доработка теста')
    def test_cache_main_page(self):
        """Тест для проверки кеширования главной страницы."""
        page = reverse('posts:index')
        before_delete = self.authorized_client.get(page)
        Post.objects.get(pk=PostViewsTests.post.pk).delete()
        after_delete = self.authorized_client.get(page)
        self.assertEqual(before_delete.content, after_delete.content)
        cache.clear()
        updated_content = self.authorized_client.get(page)
        self.assertNotEqual(after_delete.content, updated_content.content)

    def test_auth_user_can_follow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей."""
        new_author = User.objects.create_user(username='new_author')
        page = reverse(
            'posts:profile_follow',
            kwargs={'username': new_author.username}
        )
        self.authorized_client.get(page)
        self.assertTrue(
            Follow.objects.filter(
                user=PostViewsTests.author,
                author=new_author)
            .exists()
        )

    def test_auth_user_can_unfollow(self):
        """Авторизованный пользователь может
        удалять пользователей из подписок."""
        new_author = User.objects.create_user(username='new_author')
        Follow.objects.create(user=PostViewsTests.author, author=new_author)
        page = reverse(
            'posts:profile_unfollow',
            kwargs={'username': new_author.username}
        )
        self.authorized_client.get(page)
        self.assertFalse(
            Follow.objects.filter(
                user=PostViewsTests.author,
                author=new_author)
            .exists()
        )

    def test_auth_user_cant_follow_self(self):
        """Авторизованный пользователь не может
        подписаться на самого себя."""
        page = reverse(
            'posts:profile_follow',
            kwargs={'username': PostViewsTests.author.username}
        )
        self.authorized_client.get(page)
        self.assertFalse(
            Follow.objects.filter(
                user=PostViewsTests.author,
                author=PostViewsTests.author)
            .exists()
        )

    def test_auth_user_cant_double_follow(self):
        """Авторизованный пользователь не может
        еще раз подписаться на одного и того же автора."""
        new_author = User.objects.create_user(username='new_author')
        page = reverse(
            'posts:profile_follow',
            kwargs={'username': new_author.username}
        )
        self.authorized_client.get(page)
        self.authorized_client.get(page)
        self.assertEqual(
            Follow.objects.filter(
                user=PostViewsTests.author,
                author=new_author)
            .count(), 1
        )

    def test_check_subscription_feed(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        follow = User.objects.create_user(username='follow')
        follow_post = Post.objects.create(
            author=follow,
            text='Тестовый пост с подпиской',
        )
        not_follow = User.objects.create_user(username='not_follow')
        not_follow_post = Post.objects.create(
            author=not_follow,
            text='Тестовый пост без подписки',
        )
        Follow.objects.create(user=PostViewsTests.author, author=follow)
        page = reverse('posts:follow_index')
        response = self.authorized_client.get(page)
        self.assertIn('page_obj', response.context)
        page_obj = response.context['page_obj']
        self.assertIsInstance(page_obj, Page)
        self.assertIn(follow_post, page_obj)
        self.assertNotIn(not_follow_post, page_obj)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        # Спецально делаем кол-во постов больше, чем видно на странице
        cls.REMAINDER = 3
        objs = (Post(author=cls.author,
                     text=f'Тестовый пост {i}',
                     group=cls.group)
                for i in range(settings.POSTS_PER_PAGE + cls.REMAINDER))
        Post.objects.bulk_create(objs)

        # Страницы с пагинацией
        cls.pages = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': cls.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': cls.author.username}),
        ]

    def setUp(self):
        # Создаем неавторизованный клиент
        self.client = Client()

    def test_first_page_contains_fixed_records(self):
        """Проверка: количество постов на первой странице
        равно POSTS_PER_PAGE."""
        for page in PaginatorViewsTest.pages:
            with self.subTest(page=page):
                response = self.client.get(reverse('posts:index'))
                self.assertEqual(len(response.context.get('page_obj', [])),
                                 settings.POSTS_PER_PAGE)

    def test_second_page_contains_remain_records(self):
        """Проверка: на второй странице должен быть остаток постов."""
        for page in PaginatorViewsTest.pages:
            with self.subTest(page=page):
                response = self.client.get(reverse('posts:index'), {'page': 2})
                self.assertEqual(len(response.context.get('page_obj', [])),
                                 PaginatorViewsTest.REMAINDER)
