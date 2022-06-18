import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

# Временная папка для медиа-файлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):

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
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.form_data = {
            'text': 'Тестовый текст',
            'group': cls.group.pk,
            'image': cls.uploaded,
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.author)

    def test_create_post(self):
        """Валидная форма создает Post."""
        post_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=PostFormTests.form_data,
            follow=True
        )
        # Проверка: редирект для валидной формы
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': PostFormTests.author.username})
        )
        # Проверка: новый пост добавлен в базу
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверка: новый пост совпадает с формой
        self.assertTrue(
            Post.objects.filter(~Q(pk=PostFormTests.post.pk),
                                text=PostFormTests.form_data['text'],
                                group=PostFormTests.group,
                                image='posts/small.gif',
                                author=PostFormTests.author)
            .exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует Post."""
        post_count = Post.objects.count()
        PostFormTests.form_data['image'] = SimpleUploadedFile(
            name='new.gif',
            content=PostFormTests.small_gif,
            content_type='image/gif'
        )
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostFormTests.post.pk}),
            data=PostFormTests.form_data,
            follow=True
        )
        # Проверка: редирект для валидной формы
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': PostFormTests.post.pk})
        )
        # Проверка: число постов в базе не увеличилось
        self.assertEqual(Post.objects.count(), post_count)
        # Проверка: новый пост совпадает с формой
        self.assertTrue(
            Post.objects.filter(pk=PostFormTests.post.pk,
                                text=PostFormTests.form_data['text'],
                                group=PostFormTests.group,
                                image='posts/new.gif',
                                author=PostFormTests.author)
            .exists()
        )

    def test_delete_post(self):
        """Проверка формы удаления Post."""
        post_to_delete = Post.objects.create(
            author=PostFormTests.author,
            text='Тестовый пост для удаления',
            image=PostFormTests.uploaded
        )
        post_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_delete',
                    kwargs={'post_id': post_to_delete.pk}),
            follow=True
        )
        # Проверка: редирект для валидной формы
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
        # Проверка: число постов в базе уменьшилось
        self.assertEqual(Post.objects.count(), post_count - 1)
        # Проверка: не найден удаленный пост
        self.assertFalse(
            Post.objects.filter(text='Тестовый пост для удаления',
                                group=PostFormTests.group,
                                image='posts/small.gif',
                                author=PostFormTests.author)
            .exists()
        )

    def test_add_comment(self):
        """После успешной отправки комментарий появляется на странице поста."""
        form_data = {'text': 'Текст комментария'}
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': PostFormTests.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertIn('post', response.context)
        post = response.context['post']
        self.assertIsInstance(post, Post)
        self.assertTrue(
            post.comments.filter(
                post=PostFormTests.post.pk,
                text=form_data['text'],
                author=PostFormTests.author)
            .exists()
        )
