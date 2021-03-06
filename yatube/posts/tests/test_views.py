import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User
from .fixtures import FixturesData as FD

POSTS_TO_SHOW = settings.POSTS_TO_SHOW
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


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
        cls.user_1 = User.objects.create_user(
            username=FD.USER_USERNAME_1)

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
        self.authorized_client_1 = Client()
        self.authorized_author = Client()

        self.authorized_client.force_login(self.user)
        self.authorized_client_1.force_login(self.user_1)
        self.authorized_author.force_login(self.author_1)

    def check_post_present(self, url, args, post):
        """
        ????????????????, ?????? post ?????????????????? ???? ???????????? url.
        """
        response = self.guest_client.get(reverse(
            url, args=args))
        self.assertIn(post, response.context['page_obj'])

    def check_post_not_present(self, url, args, post):
        """
        ????????????????, ?????? post ???? ?????????????????? ???? ???????????? url.
        """
        response = self.guest_client.get(reverse(
            url, args=args))
        self.assertNotIn(post, response.context['page_obj'])

    def test_cache_index(self):
        """
        ???????? ??????????????????????.
        """
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
        """
        ????????????????????????, ?????? ????????1, ?? ???????????????? ??????????1 ?? ????????????1
        ?????????? ?? ???????????? ???????????????? ???? ??????????????????.
        """
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
        """
        ???????????????????????? ?????????????????? ?????????????? ????????????????
        """
        response = self.guest_client.get(reverse('posts:home_page'))
        self.assertIn(self.post_1, response.context['page_obj'])
        self.assertIn(self.post_2, response.context['page_obj'])
        self.assertIn(self.post_3, response.context['page_obj'])

    def test_context_group_list(self):
        """
        ???????????????????????? ?????????????????? ????????????
        """
        response = self.guest_client.get(reverse(
            'posts:group_list', args=(FD.TEST_GROUP_SLUG_1,)))
        for obj in response.context['page_obj']:
            with self.subTest(obj=obj):
                self.assertEqual(obj.group.slug, FD.TEST_GROUP_SLUG_1)

    def test_context_profile(self):
        """
        ???????????????????????? ?????????????????? ??????????????.
        """
        response = self.guest_client.get(reverse(
            'posts:profile', args=(FD.AUTHOR_USERNAME_2,)))
        for obj in response.context['page_obj']:
            with self.subTest(obj=obj):
                self.assertEqual(obj.author.username, FD.AUTHOR_USERNAME_2)

    def test_context_post_detail(self):
        """
        ???????????????? ?????????????????? ??????????.
        """
        post_pk = self.post_3.pk
        response = self.guest_client.get(reverse(
            'posts:post_detail', args=(post_pk,)))
        responsed_pk = response.context['post'].pk
        responsed_text = response.context['post'].text

        # ???????????????? ???????????????????????????? ?????????? ?? ????????????, ?????? ???????????? ?? pk
        self.assertFalse(hasattr(response.context['post'], "__getitem__"))
        self.assertEqual(responsed_text, self.post_3.text)
        self.assertEqual(responsed_pk, post_pk)

    def test_context_create_post(self):
        """
        ???????????????? ?????????????????? ?????????? ???????????????? ??????????.
        """
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
        """
        ???????????????? ?????????????????? ?????????? ???????????????????????????? ??????????.
        """
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

    def test_context_follows(self):
        """
        ?????????? ???????????? ???????????????????????? ????????????????????
        ?? ?????????? ??????, ?????? ???? ???????? ???????????????? ?? ????
        ???????????????????? ?? ?????????? ??????, ?????? ???? ????????????????.
        """
        # user
        self.authorized_client.get(
            reverse('posts:profile_follow', args=(
                self.author_1.username,))
        )
        # user
        response_follow = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        # user_1
        response_nofollow = self.authorized_client_1.get(
            reverse('posts:follow_index')
        )
        self.assertIn(self.post_1, response_follow.context['page_obj'])
        self.assertNotIn(self.post_1, response_nofollow.context['page_obj'])

    def test_follows(self):
        """???????? ?????? ???????? ???????????????????? ?? ?????????????????? ???? ????????????"""
        self.assertFalse(
            self.author_1.following.filter(user=self.user).exists()
        )
        self.authorized_client.get(
            reverse('posts:profile_follow', args=(
                self.author_1.username,))
        )
        self.assertTrue(
            self.author_1.following.filter(user=self.user).exists()
        )
        self.authorized_client.get(
            reverse('posts:profile_unfollow', args=(
                self.author_1.username,))
        )
        self.assertFalse(
            self.author_1.following.filter(user=self.user).exists()
        )


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
        """
        ?????????????? ???????????????????????? ?????????????????????? ?????????????? ?? ????????????????
        ?? ???????????????????????????? reverse.
        """
        for url_rev in urls.keys():
            args, code, template, url = urls[url_rev]
            with self.subTest(url=url_rev):
                response = client.get(reverse(url_rev, args=args))
                self.assertEqual(response.status_code, code)
                if template is not None:
                    self.assertTemplateUsed(response, template)

    def test_templates(self):
        """
        ???????????????????????? ???????????????? ?? ??????????????
        ?? ???????????????????????????? reverse.
        """
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
        """
        ???????????????????????? ??????????????????????.
        """
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


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageViewsTest(TestCase):
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

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=FD.TEST_IMAGE,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text=FD.TEST_POST_TEXT_1,
            group=cls.group,
            author=cls.author,
            image=uploaded
        )
        cls.post_id = cls.post.pk

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_image_home(self):
        """
        ???????? ???????????????? ???? ?????????????? ????????????????.
        """
        response = self.guest_client.get(reverse('posts:home_page'))
        self.assertEqual(
            response.context['page_obj'][0].image,
            self.post.image,
        )

    def test_image_profile(self):
        """
        ???????? ???????????????? ???? ???????????????? ????????????.
        """
        response = self.guest_client.get(
            reverse('posts:profile', args=(self.author.username,))
        )
        self.assertEqual(
            response.context['page_obj'][0].image,
            self.post.image,
        )

    def test_image_group(self):
        """
        ???????? ???????????????? ???? ???????????????? ????????????.
        """
        response = self.guest_client.get(
            reverse('posts:group_list', args=(self.group.slug,))
        )
        self.assertEqual(
            response.context['page_obj'][0].image,
            self.post.image,
        )

    def test_image_post_detail(self):
        """
        ???????? ???????????????? ???? ???????????????? ??????????.
        """
        response = self.guest_client.get(
            reverse('posts:post_detail', args=(self.post_id,))
        )
        self.assertEqual(
            response.context['post'].image,
            self.post.image,
        )
