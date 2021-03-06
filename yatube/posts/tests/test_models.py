from django.test import TestCase

from ..models import Group, Post, User, Comment, Follow
from .fixtures import FixturesData as FD

from django.db.utils import IntegrityError


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=FD.USER_USERNAME)
        cls.group = Group.objects.create(
            title=FD.TEST_GROUP_TITLE_1,
            slug=FD.TEST_GROUP_SLUG_1,
            description=FD.TEST_GROUP_DESCRIPTION_1,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=FD.TEST_POST_TEXT_1,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=FD.TEST_POST_TEXT_1
        )
        cls.author = User.objects.create_user(username=FD.AUTHOR_USERNAME_1)
        cls.follow = Follow(
            user=cls.user,
            author=cls.author
        )

    def test_models_have_correct_object_names(self):
        """
        Проверяем, что у моделей корректно работает __str__.
        """
        group = self.group
        post = self.post
        comment = self.comment
        follow = self.follow

        objects_names = {
            str(group): group.title,
            str(post): post.text[:15],
            str(comment): comment.text[:15],
            str(follow): (
                f'{self.user.username}->{self.author.username}'
            ),
        }

        for value, expected in objects_names.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_follow_unique_constrait(self):
        """
        Проверяем, что нельзя дважды подписаться на одного автора.
        """
        with self.assertRaises(
            IntegrityError,
        ) as context:
            Follow(
                user=self.user,
                author=self.author
            ).save()
            Follow(
                user=self.user,
                author=self.author
            ).save()
        self.assertTrue('UNIQUE constraint failed' in str(context.exception))

    def test_follow_equal_constrait(self):
        """
        Проверяем, что нельзя подписаться на самого себя.
        """
        with self.assertRaises(
            IntegrityError,
        ) as context:
            Follow(
                user=self.user,
                author=self.user
            ).save()
        self.assertTrue('CHECK constraint failed' in str(context.exception))
