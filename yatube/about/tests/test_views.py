from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pages = [
            reverse('about:author'),
            reverse('about:tech'),
        ]
        cls.templates_pages = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }

    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени about, доступен."""
        for page in AboutViewsTests.pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_uses_correct_template(self):
        """При запросе к about применяется нужный шаблон."""
        for template, page in AboutViewsTests.templates_pages.items():
            with self.subTest(template=template):
                response = self.guest_client.get(page)
                self.assertTemplateUsed(response, template)
