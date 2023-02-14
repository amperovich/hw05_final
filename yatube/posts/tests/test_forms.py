from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker
from mixer.backend.django import mixer

from posts.models import Comment, Post

User = get_user_model()
fake = Faker()


class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)

        cls.auth = Client()
        cls.auth.force_login(cls.user)

    def test_create_post_by_auth_user(self):
        self.group = mixer.blend('posts.Group')
        data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
        }
        response = self.auth.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user},
            ),
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        context = response.context.get('post')
        self.assertEqual(
            post.pk,
            context.pk,
        )
        self.assertEqual(
            post.text,
            context.text,
        )

    def test_edit_post_by_author(self):
        self.author_user = mixer.blend(User)
        self.auth_author = Client()
        self.auth_author.force_login(self.author_user)

        self.group = mixer.blend('posts.Group')
        self.post = mixer.blend('posts.Post', author=self.author_user)
        data = {
            'group': self.group.id,
            'text': 'Новый текст',
        }
        response = self.auth_author.post(
            reverse(
                'posts:post_edit',
                kwargs={'pk': self.post.pk},
            ),
            data=data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'pk': self.post.id},
            ),
        )
        post = Post.objects.first()
        context = response.context.get('post')
        self.assertEqual(
            post.pk,
            context.pk,
        )
        self.assertEqual(
            post.text,
            context.text,
        )

    def test_create_post_by_anon(self):
        response = self.client.post(
            reverse('posts:post_create'),
            data={'text': 'Тестовый текст'},
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)
        self.assertIsNone(response.context.get('post'))

    def test_edit_post_by_anon(self):
        self.author_user = mixer.blend(User)
        self.post = mixer.blend('posts.Post', author=self.author_user)
        response = self.client.post(
            reverse(
                'posts:post_edit',
                kwargs={'pk': self.post.pk},
            ),
            data={'text': 'Тестовый текст'},
            follow=True,
        )
        self.assertIsNone(response.context.get('post'))

    def test_edit_post_by_non_author_auth_user(self):
        self.author_user = mixer.blend(User)
        self.post = mixer.blend('posts.Post', author=self.author_user)
        data = {
            'text': 'Новый текст',
        }
        response = self.auth.post(
            reverse(
                'posts:post_edit',
                kwargs={'pk': self.post.pk},
            ),
            data=data,
            follow=True,
        )
        self.assertEqual(
            Post.objects.get().text,
            response.context.get('post').text,
        )

    def test_create_comment(self):
        self.author_user = mixer.blend(User)
        self.post = mixer.blend('posts.Post', author=self.author_user)
        data = {
            'text': fake.pystr(min_chars=3, max_chars=50),
            'author': self.post.author,
            'post': self.post.pk,
        }
        response = self.auth.post(
            reverse(
                'posts:add_comment',
                kwargs={'pk': self.post.pk},
            ),
            data=data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'pk': self.post.pk},
            ),
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.get()
        context = response.context.get('comments')[0]
        self.assertEqual(
            comment.pk,
            context.pk,
        )
        self.assertEqual(
            comment.text,
            context.text,
        )
