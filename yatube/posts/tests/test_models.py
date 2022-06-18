from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для проверки',
        )
        cls.model_field_verboses = {
            Group: {
                'title': 'Название группы',
                'slug': 'URL группы',
            },
            Post: {
                'text': 'Текст поста',
                'pub_date': 'Дата публикации',
                'author': 'Пользователь',
                'group': 'Группа',
                'image': 'Картинка',
            },
        }
        cls.model_field_help_texts = {
            Group: {
                'title': 'Введите название группы',
                'slug': 'Введите URL группы',
            },
            Post: {
                'text': 'Введите текст поста',
                'pub_date': 'Введите дату публикации',
                'author': 'Введите имя пользователя',
                'group': 'Введите название группы',
                'image': 'Добавьте картинку',
            },
        }
        cls.model_titles = {
            cls.group: cls.group.title,
            cls.post: cls.post.text[:15],
        }

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        for model, field in PostModelTest.model_field_verboses.items():
            for value, expected in field.items():
                with self.subTest(value=value):
                    self.assertEqual(
                        model._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        for model, field in PostModelTest.model_field_help_texts.items():
            for value, expected in field.items():
                with self.subTest(value=value):
                    self.assertEqual(
                        model._meta.get_field(value).help_text, expected)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        for model, expected_name in PostModelTest.model_titles.items():
            with self.subTest(model=model):
                self.assertEqual(expected_name, str(model))
