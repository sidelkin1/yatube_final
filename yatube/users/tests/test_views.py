from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import UserCreationForm

User = get_user_model()


class UserViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.pages_templates = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент-автор
        self.authorized_client = Client()
        self.authorized_client.force_login(UserViewsTests.user)

    def test_reverse_uses_correct_template(self):
        """reverse использует соответствующий шаблон."""
        for reverse_name, template in UserViewsTests.pages_templates.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_form_show_correct_context(self):
        """Шаблон регистрации сформированы с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('users:signup')
        )
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIsInstance(form, UserCreationForm)
