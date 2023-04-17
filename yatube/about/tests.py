from django.test import TestCase, Client
from http import HTTPStatus
from django.contrib.auth import get_user_model


User = get_user_model()


class AboutPagesURLTests(TestCase):
    def setUp(self):
        # Создаем неавторизованый клиент
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Mangekos')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов /about/."""
        templates_url = [
            '/about/author/',
            '/about/tech/',
        ]
        for address in templates_url:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_auth_url_exists_at_desired_location(self):
        """Проверка доступности адресов /about/."""
        templates_url = [
            '/about/author/',
            '/about/tech/',
        ]
        for address in templates_url:
            response = self.authorized_client.get(address)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для адресов /about/."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
