from http import HTTPStatus

from django.test import Client, TestCase
from django.core.cache import cache

from ..models import Group, Post, User
from .fixtures import FixturesData as FD


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.fixtures = FD()

        cls.author = User.objects.create_user(
            username=FD.AUTHOR_USERNAME_1)
        cls.user = User.objects.create_user(
            username=FD.USER_USERNAME)
        cls.group = Group.objects.create(
            title=FD.TEST_GROUP_TITLE_1,
            slug=FD.TEST_GROUP_SLUG_1,
            description=FD.TEST_GROUP_DESCRIPTION_1
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text=FD.TEST_POST_TEXT_1
        )

        cls.fixtures.make_dict_url(cls.post, cls.group)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(URLTests.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(URLTests.author)

    def test_404(self):
        """Проверка страницы 404."""
        response = self.guest_client.get('unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def check_urls_templates(self, urls, client):
        """Функция тестирования доступности адресов и шаблонов."""
        for key in urls.keys():
            args, code, template, url = urls[key]
            with self.subTest(key=key):
                response = client.get(url)
                self.assertEqual(response.status_code, code)
                if template is not None:
                    self.assertTemplateUsed(response, template)

    def test_unauthorized_access(self):
        """Проверка доступности адресов для
        неавторизованного пользователя и шаблонов."""
        self.check_urls_templates(self.fixtures.URLS_UNAUTHORIZED, self.guest_client)

    def test_authorized_access(self):
        """Проверка доступности адресов для авторизованного пользователя."""
        self.check_urls_templates(self.fixtures.URLS_AUTHORIZED, self.authorized_client)

    def test_author_access(self):
        """Проверка доступности адресов для автора поста."""
        self.check_urls_templates(self.fixtures.URLS_AUTHOR, self.authorized_author)
