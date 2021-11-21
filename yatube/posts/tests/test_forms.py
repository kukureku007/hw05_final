from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from .fixtures_posts import FixturesData as FD


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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_post_create_edit(self):
        """Тестирование форм создания и редактирования поста.
        Сначала создаём пост, потом его редактируем."""
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

        post_id = post.first().pk
        form_data = {
            'text': FD.TEST_POST_EDIT,
            'group': PostsFormsTests.group_2.id,
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