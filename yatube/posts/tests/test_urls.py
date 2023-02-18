from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker
from mixer.backend.django import mixer

User = get_user_model()
fake = Faker()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user, cls.author_user = mixer.cycle(2).blend(
            User,
            username=(name for name in ('user', 'author')),
        )

        cls.auth = Client()
        cls.auth.force_login(cls.user)

        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author_user)

        cls.group = mixer.blend('posts.Group')
        cls.post = mixer.blend('posts.Post', author=cls.author_user)

        cls.urls = {
            'comment': reverse('posts:add_comment', args=(cls.post.pk,)),
            'follow': reverse('posts:follow_index'),
            'group': reverse('posts:group_list', args=(cls.group.slug,)),
            'index': reverse('posts:index'),
            'login': reverse('users:login'),
            'post_create': reverse('posts:post_create'),
            'post_detail': reverse('posts:post_detail', args=(cls.post.pk,)),
            'post_edit': reverse('posts:post_edit', args=(cls.post.pk,)),
            'profile': reverse('posts:profile', args=(cls.post.author,)),
            'profile_follow': reverse(
                'posts:profile_follow',
                args=(cls.post.author.username,),
            ),
            'profile_unfollow': reverse(
                'posts:profile_unfollow',
                args=(cls.post.author.username,),
            ),
            'nonexistent': fake.pystr(min_chars=3, max_chars=13),
        }

        cls.clients = {
            cls.auth: 'User',
            cls.auth_author: 'Author',
        }

    def setUp(self):
        cache.clear()

    def test_http_statuses(self):
        http_statuses = (
            ('comment', HTTPStatus.FOUND, self.client),
            ('comment', HTTPStatus.FOUND, self.auth),
            ('follow', HTTPStatus.FOUND, self.client),
            ('follow', HTTPStatus.OK, self.auth),
            ('follow', HTTPStatus.OK, self.auth_author),
            ('group', HTTPStatus.OK, self.client),
            ('index', HTTPStatus.OK, self.client),
            ('login', HTTPStatus.OK, self.client),
            ('post_create', HTTPStatus.FOUND, self.client),
            ('post_create', HTTPStatus.OK, self.auth),
            ('post_detail', HTTPStatus.OK, self.client),
            ('post_edit', HTTPStatus.FOUND, self.client),
            ('post_edit', HTTPStatus.FOUND, self.auth),
            ('post_edit', HTTPStatus.OK, self.auth_author),
            ('profile_follow', HTTPStatus.FOUND, self.client),
            ('profile_follow', HTTPStatus.FOUND, self.auth),
            ('profile_unfollow', HTTPStatus.FOUND, self.client),
            ('profile_unfollow', HTTPStatus.FOUND, self.auth),
            ('profile', HTTPStatus.OK, self.auth),
            ('nonexistent', HTTPStatus.NOT_FOUND, self.auth),
        )
        for url, status_code, client in http_statuses:
            with self.subTest(
                url=url,
                status_code=status_code,
                client=self.clients.get(client, 'Anon'),
            ):
                self.assertEqual(
                    client.get(self.urls.get(url)).status_code,
                    status_code.value,
                )

    def test_templates(self):
        templates = (
            (
                self.urls.get('group'),
                'posts/group_list.html',
                self.client,
            ),
            (
                self.urls.get('follow'),
                'posts/follow.html',
                self.auth,
            ),
            (
                self.urls.get('index'),
                'posts/index.html',
                self.client,
            ),
            (
                self.urls.get('login'),
                'users/login.html',
                self.client,
            ),
            (
                self.urls.get('post_create'),
                'posts/create_post.html',
                self.auth,
            ),
            (
                self.urls.get('post_detail'),
                'posts/post_detail.html',
                self.client,
            ),
            (
                self.urls.get('post_edit'),
                'posts/create_post.html',
                self.auth_author,
            ),
            (
                self.urls.get('profile'),
                'posts/profile.html',
                self.client,
            ),
        )
        for url, template, client in templates:
            with self.subTest(
                url=url,
                template=template,
                client=self.clients.get(client, 'Anon'),
            ):
                self.assertTemplateUsed(client.get(url), template)

    def test_redirects(self):
        redirects = (
            (
                self.urls.get('comment'),
                redirect_to_login(self.urls.get('comment')).url,
                self.client,
            ),
            (
                self.urls.get('comment'),
                self.urls.get('post_detail'),
                self.auth,
            ),
            (
                self.urls.get('post_create'),
                redirect_to_login(self.urls.get('post_create')).url,
                self.client,
            ),
            (
                self.urls.get('post_edit'),
                redirect_to_login(self.urls.get('post_edit')).url,
                self.client,
            ),
            (
                self.urls.get('post_edit'),
                self.urls.get('post_detail'),
                self.auth,
            ),
            (
                self.urls.get('profile_follow'),
                redirect_to_login(self.urls.get('profile_follow')).url,
                self.client,
            ),
            (
                self.urls.get('profile_follow'),
                self.urls.get('profile', (self.post.author.username,)),
                self.auth,
            ),
            (
                self.urls.get('profile_follow'),
                self.urls.get('profile', (self.post.author.username,)),
                self.auth_author,
            ),
            (
                self.urls.get('profile_unfollow'),
                redirect_to_login(self.urls.get('profile_unfollow')).url,
                self.client,
            ),
            (
                self.urls.get('profile_unfollow'),
                self.urls.get('profile', (self.post.author.username,)),
                self.auth,
            ),
        )
        for url, redirect, client in redirects:
            with self.subTest(
                url=url,
                redirect=redirect,
                client=self.clients.get(client, 'Anon'),
            ):
                self.assertRedirects(
                    client.get(url),
                    redirect,
                )
