from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form_data = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'username': 'username',
            'email': 'username@example.com',
            'password1': 'B;tdcr64',
            'password2': 'B;tdcr64',
        }

    def setUp(self):
        # Создаем авторизованый клиент
        self.client = Client()

    def test_create_user(self):
        """Валидная форма создает User."""
        user_count = User.objects.count()
        response = self.client.post(
            reverse('users:signup'),
            data=UserFormTests.form_data,
            follow=True
        )
        # Проверка: редирект для валидной формы
        self.assertRedirects(response, reverse('posts:index'))
        # Проверка: новый пост добавлен в базу
        self.assertEqual(User.objects.count(), user_count + 1)
        # Проверка: новый пост совпадает с формой
        self.assertTrue(
            User.objects.filter(
                first_name=UserFormTests.form_data['first_name'],
                last_name=UserFormTests.form_data['last_name'],
                username=UserFormTests.form_data['username'],
                email=UserFormTests.form_data['email'])
            .exists()
        )
