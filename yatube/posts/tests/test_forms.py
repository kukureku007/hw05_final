import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User
from .fixtures import FixturesData as FD

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(
            username=FD.AUTHOR_USERNAME_1)

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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_post_create_edit(self):
        """
        Тестирование форм создания и редактирования поста.
        Сначала создаём пост, потом его редактируем
        Добавлен тест картинок.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': FD.TEST_POST_TEXT_1,
            'group': self.group_1.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:profile', args=(FD.AUTHOR_USERNAME_1,)))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.filter(
            text=FD.TEST_POST_TEXT_1,
            group=self.group_1,
            author=self.author
        )
        self.assertTrue(
            post.exists()
        )

        # При редактировании добавляем картинку
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=FD.TEST_IMAGE,
            content_type='image/gif'
        )

        post_id = post.first().pk
        form_data = {
            'text': FD.TEST_POST_EDIT,
            'group': PostsFormsTests.group_2.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(post_id,)),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail', args=(post_id,)))
        self.assertEqual(Post.objects.count(), posts_count + 1)

        post_edited = Post.objects.get(
            pk=post_id
        )
        self.assertEqual(post_edited.text, FD.TEST_POST_EDIT)
        self.assertEqual(post_edited.group, self.group_2)
        self.assertEqual(post_edited.author, self.author)
        self.assertEqual(post_edited.image, 'posts/small.gif')


class CommentFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(
            username=FD.AUTHOR_USERNAME_1)
        cls.author = User.objects.create_user(
            username=FD.USER_USERNAME)
        cls.post = Post.objects.create(
            text=FD.TEST_POST_TEXT_1,
            author=cls.author,
        )
        cls.post_id = Post.objects.first().pk
        cls.comment_url = reverse('posts:add_comment', args=(cls.post_id,))

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_authorized_comment(self):
        """
        Авторизованный пользователь может оставить комментарий к посту,
        этот комментарий сохранится и отобразится
        """
        comments_count = self.post.comments.count()

        form_data = {
            'text': FD.TEST_POST_TEXT_1,
        }
        response = self.authorized_client.post(
            self.comment_url,
            data=form_data,
            follow=True
        )
        self.assertEqual(self.post.comments.count(), comments_count + 1)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post_id,))
        )
        response = self.guest_client.get(
            reverse('posts:post_detail', args=(self.post_id,))
        )
        self.assertIn(
            self.post.comments.first(),
            response.context['post'].comments.all()
        )
