from django.test import TestCase

from ..models import Group, Post, User
from .fixtures import FixturesData as FD


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=FD.AUTHOR_USERNAME_1)
        cls.group = Group.objects.create(
            title=FD.TEST_GROUP_TITLE_1,
            slug=FD.TEST_GROUP_SLUG_1,
            description=FD.TEST_GROUP_DESCRIPTION_1,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=FD.TEST_POST_TEXT_1,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post

        objects_names = {
            str(group): group.title,
            str(post): post.text[:15],
        }

        for value, expected in objects_names.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
