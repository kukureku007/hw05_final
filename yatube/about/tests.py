from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    urls = (
        ('about:author', '/about/author/', 'about/author.html', HTTPStatus.OK),
        ('about:tech', '/about/tech/', 'about/tech.html', HTTPStatus.OK),
    )

    def setUp(self):
        # Создаем неавторизованый клиент
        self.guest_client = Client()

    def test_staticpages_url_template(self):
        for item in self.urls:
            url_reverse, url, template, code = item
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, code)
                self.assertTemplateUsed(response, template)
                response = self.client.get(reverse(url_reverse))
                self.assertEqual(response.status_code, code)
                self.assertTemplateUsed(response, template)
