from django import forms
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from django.core.cache import cache

from ..models import Group, Post, User
from .fixtures import FixturesData as FD

POSTS_TO_SHOW = settings.POSTS_TO_SHOW


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author_1 = User.objects.create_user(
            username=FD.AUTHOR_USERNAME_1)
        cls.author_2 = User.objects.create_user(
            username=FD.AUTHOR_USERNAME_2)
        cls.user = User.objects.create_user(
            username=FD.USER_USERNAME)

        cls.group_1 = Group.objects.create(
            title=FD.TEST_GROUP_TITLE_1,
            slug=FD.TEST_GROUP_SLUG_1,
            description=FD.TEST_GROUP_DESCRIPTION_1
        )
        cls.group_2 = Group.objects.create(
            title=FD.TEST_GROUP_TITLE_2,
            slug=FD.TEST_GROUP_SLUG_2,
            description=FD.TEST_GROUP_DESCRIPTION_2
        )

        cls.post_1 = Post.objects.create(
            author=cls.author_1,
            text=FD.TEST_POST_TEXT_1,
            group=cls.group_1
        )
        cls.post_2 = Post.objects.create(
            author=cls.author_2,
            text=FD.TEST_POST_TEXT_2,
            group=cls.group_2
        )
        cls.post_3 = Post.objects.create(
            author=cls.author_2,
            text=FD.TEST_POST_WO_GROUP_TEXT,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_author = Client()

        self.authorized_client.force_login(self.user)
        self.authorized_author.force_login(self.author_1)

    def check_post_present(self, url, args, post):
        """Проверка, что post находится по адресу url."""
        response = self.guest_client.get(reverse(
            url, args=args))
        self.assertIn(post, response.context['page_obj'])

    def check_post_not_present(self, url, args, post):
        """Проверка, что post не находится по адресу url."""
        response = self.guest_client.get(reverse(
            url, args=args))
        self.assertNotIn(post, response.context['page_obj'])

    def test_cache_index(self):
        """Тест кэширования."""
        post = Post.objects.create(
            author=self.author_1,
            text=FD.TEST_POST_CACHE,
            group=self.group_1
        )
        response = self.guest_client.get(reverse('posts:home_page'))
        self.assertIn(FD.TEST_POST_CACHE, response.content.decode())
        post.delete()
        response = self.guest_client.get(reverse('posts:home_page'))
        self.assertIn(FD.TEST_POST_CACHE, response.content.decode())
        cache.clear()
        response = self.guest_client.get(reverse('posts:home_page'))
        self.assertNotIn(FD.TEST_POST_CACHE, response.content.decode())

    def test_post_present(self):
        """Тестирование, что Пост1, у которого Автор1 и Группа1
        попал в нужный контекст на страницах."""
        self.check_post_present('posts:home_page', None, self.post_1)
        self.check_post_present('posts:group_list', (
            FD.TEST_GROUP_SLUG_1,), self.post_1)
        self.check_post_present('posts:profile', (
            FD.AUTHOR_USERNAME_1,), self.post_1)
        self.check_post_not_present('posts:group_list', (
            FD.TEST_GROUP_SLUG_2,), self.post_1)
        self.check_post_not_present('posts:profile', (
            FD.AUTHOR_USERNAME_2,), self.post_1)

    def test_context_index(self):
        """Тестирование контекста главной страницы"""
        response = self.guest_client.get(reverse('posts:home_page'))
        self.assertIn(self.post_1, response.context['page_obj'])
        self.assertIn(self.post_2, response.context['page_obj'])
        self.assertIn(self.post_3, response.context['page_obj'])

    def test_context_group_list(self):
        """Тестирование контекста группы"""
        response = self.guest_client.get(reverse(
            'posts:group_list', args=(FD.TEST_GROUP_SLUG_1,)))
        for obj in response.context['page_obj']:
            with self.subTest(obj=obj):
                self.assertEqual(obj.group.slug, FD.TEST_GROUP_SLUG_1)

    def test_context_profile(self):
        """Тестирование контекста профиля"""
        response = self.guest_client.get(reverse(
            'posts:profile', args=(FD.AUTHOR_USERNAME_2,)))
        for obj in response.context['page_obj']:
            with self.subTest(obj=obj):
                self.assertEqual(obj.author.username, FD.AUTHOR_USERNAME_2)

    def test_context_post_detail(self):
        """Проверка контекста поста."""
        post_pk = self.post_3.pk
        response = self.guest_client.get(reverse(
            'posts:post_detail', args=(post_pk,)))
        responsed_pk = response.context['post'].pk
        responsed_text = response.context['post'].text

        # Проверка единственности поста в ответе, его текста и pk
        self.assertFalse(hasattr(response.context['post'], "__getitem__"))
        self.assertEqual(responsed_text, self.post_3.text)
        self.assertEqual(responsed_pk, post_pk)

    def test_context_create_post(self):
        """Проверка контекста формы создания поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_context_edit_post(self):
        """Проверка контекста формы редоктирования поста."""
        post_pk = self.post_1.pk
        response = self.authorized_author.get(reverse(
            'posts:post_edit', args=[post_pk]))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class TemplateViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.fixtures = FD()

        cls.author_1 = User.objects.create_user(
            username=FD.AUTHOR_USERNAME_1)
        cls.author_2 = User.objects.create_user(
            username=FD.AUTHOR_USERNAME_2)
        cls.user = User.objects.create_user(
            username=FD.USER_USERNAME)

        cls.group_1 = Group.objects.create(
            title=FD.TEST_GROUP_TITLE_1,
            slug=FD.TEST_GROUP_SLUG_1,
            description=FD.TEST_GROUP_DESCRIPTION_1
        )
        cls.group_2 = Group.objects.create(
            title=FD.TEST_GROUP_TITLE_2,
            slug=FD.TEST_GROUP_SLUG_2,
            description=FD.TEST_GROUP_DESCRIPTION_2
        )

        cls.post_1 = Post.objects.create(
            author=cls.author_1,
            text=FD.TEST_POST_TEXT_1,
            group=cls.group_1
        )
        cls.post_2 = Post.objects.create(
            author=cls.author_2,
            text=FD.TEST_POST_TEXT_2,
            group=cls.group_2
        )
        cls.post_3 = Post.objects.create(
            author=cls.author_2,
            text=FD.TEST_POST_WO_GROUP_TEXT,
        )

        cls.fixtures.make_dict(cls.post_1, cls.group_1)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_author = Client()

        self.authorized_client.force_login(self.user)
        self.authorized_author.force_login(self.author_1)

    def check_reverse_urls_templates(self, urls, client):
        """Функция тестирования доступности адресов и шаблонов
        с использованием reverse."""
        for url_rev in urls.keys():
            args, code, template, url = urls[url_rev]
            with self.subTest(url=url_rev):
                response = client.get(reverse(url_rev, args=args))
                self.assertEqual(response.status_code, code)
                if template is not None:
                    self.assertTemplateUsed(response, template)

    def test_templates(self):
        """Тестирование шаблонов и адресов
        с использованием reverse."""
        self.check_reverse_urls_templates(
            self.fixtures.URLS_UNAUTHORIZED, self.guest_client)
        self.check_reverse_urls_templates(
            self.fixtures.URLS_AUTHORIZED, self.authorized_client)
        self.check_reverse_urls_templates(
            self.fixtures.URLS_AUTHOR, self.authorized_author)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username=FD.AUTHOR_USERNAME_1)
        cls.group = Group.objects.create(
            title=FD.TEST_GROUP_TITLE_1,
            slug=FD.TEST_GROUP_SLUG_1,
            description=FD.TEST_GROUP_DESCRIPTION_1
        )
        for i in range(0, FD.POST_NUM):
            cls.post_1 = Post.objects.create(
                author=cls.author,
                text=FD.POST_TEXT + str(i),
                group=cls.group
            )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_paginator_page(self):
        """Тестирование паджинатора"""
        for url in FD.URLS_PAGINATOR.keys():
            with self.subTest(url=url):
                response = self.client.get(reverse(
                    url, args=FD.URLS_PAGINATOR[url]))
                self.assertEqual(len(response.context['page_obj']),
                                 POSTS_TO_SHOW)
                response = self.client.get(reverse(
                    url, args=FD.URLS_PAGINATOR[url]) + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 FD.POST_NUM - POSTS_TO_SHOW)
