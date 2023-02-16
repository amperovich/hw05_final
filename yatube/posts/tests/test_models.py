from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from mixer.backend.django import mixer

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = mixer.blend('posts.Post')

    def test_models_have_correct_object_post(self):
        self.assertEquals(
            self.post.text[:settings.STRING_SIZE],  # fmt: skip
            str(self.post)[:settings.STRING_SIZE],  # fmt: skip
        )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend('posts.Group')

    def test_models_have_correct_object_group(self):
        self.assertEquals(
            self.group.title,
            str(self.group),
        )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.comment = mixer.blend('posts.Comment')

    def test_models_have_correct_object_group(self):
        self.assertEquals(
            self.comment.text[:settings.STRING_SIZE],  # fmt: skip
            str(self.comment)[:settings.STRING_SIZE],  # fmt: skip
        )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follow = mixer.blend('posts.Follow')

    def test_models_have_correct_object_group(self):
        self.assertEquals(
            f'{self.follow.user} подписан на {self.follow.author}',
            str(self.follow),
        )
