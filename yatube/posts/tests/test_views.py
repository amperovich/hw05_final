from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Follow, Post

User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.cycle(2).blend(User)

        cls.auth_author = Client()
        cls.auth_author.force_login(cls.user[0])

        cls.auth = Client()
        cls.auth.force_login(cls.user[1])

        cls.group = mixer.cycle(2).blend('posts.Group')

        cls.post = mixer.blend('posts.Post', author=cls.user[0])

        cls.form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        cls.templates_pages_names = {
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/follow.html': reverse('posts:follow_index'),
            'posts/group_list.html': (
                reverse(
                    'posts:group_list',
                    kwargs={'slug': cls.group[0].slug},
                )
            ),
            'posts/index.html': reverse('posts:index'),
            'posts/profile.html': (
                reverse(
                    'posts:profile',
                    kwargs={'username': cls.user[0]},
                )
            ),
            'posts/post_detail.html': (
                reverse(
                    'posts:post_detail',
                    kwargs={'pk': cls.post.id},
                )
            ),
        }

    def setUp(self):
        cache.clear()

    def test_pages_use_correct_templates(self):
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_displays_correct_context(self):
        response = self.auth.get(reverse('posts:post_create'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(
                    value,
                )
                self.assertIsInstance(
                    form_field,
                    expected,
                )

    def test_post_edit_displays_correct_context(self):
        response = self.auth_author.get(
            reverse(
                'posts:post_edit',
                kwargs={'pk': self.post.pk},
            ),
        )
        for value, expected in self.form_fields.items():
            with self.subTest(
                value=value,
                expected=expected,
            ):
                form_field = response.context.get('form').fields.get(
                    value,
                )
                self.assertIsInstance(
                    form_field,
                    expected,
                )

    def test_group_list_displays_correct_context(self):
        response = self.auth.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group[0].slug},
            ),
        )
        self.assertEqual(
            response.context.get('group').title,
            self.group[0].title,
        )
        self.assertEqual(
            response.context.get('group').slug,
            self.group[0].slug,
        )
        self.assertEqual(
            response.context.get('group').description,
            self.group[0].description,
        )

    def test_pages_with_post_data_display_correct_context(self):
        for template, reverse_name in self.templates_pages_names.items():
            if template in (
                'posts/index.html',
                'posts/profile.html',
                'posts/post_detail.html',
            ):
                response = self.auth.get(reverse_name)
                self.assertEqual(
                    response.context.get('post').author,
                    self.post.author,
                )
                self.assertEqual(
                    response.context.get('post').pub_date,
                    self.post.pub_date,
                )
                self.assertEqual(
                    response.context.get('post').text,
                    self.post.text,
                )

    def test_post_assigned_to_a_propper_group(self):
        new_post = Post.objects.create(
            group=self.group[0],
            author=self.user[0],
            text='Ещё один пост',
        )
        for template, reverse_name in self.templates_pages_names.items():
            if template in (
                'posts/index.html',
                'posts/group_list.html',
                'posts/profile.html',
            ):
                response = self.auth.get(reverse_name)
                self.assertIn(
                    new_post,
                    response.context.get('page_obj').object_list,
                )

    def test_auth_can_follow(self):
        self.assertFalse(
            Follow.objects.filter(
                user=self.user[1],
                author=self.user[0],
            ).exists(),
        )
        self.auth.get(
            reverse(
                'posts:profile_follow',
                args=(self.post.author.username,),
            ),
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user[1],
                author=self.user[0],
            ).exists(),
        )

    def test_auth_can_unfollow(self):
        Follow.objects.create(
            user=self.user[1],
            author=self.user[0],
        )
        self.auth.get(
            reverse(
                'posts:profile_unfollow',
                args=(self.post.author.username,),
            ),
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user[1],
                author=self.user[0],
            ).exists(),
        )

    def test_auth_cant_follow_twice(self):
        Follow.objects.create(
            user=self.user[1],
            author=self.user[0],
        )
        self.auth.get(
            reverse(
                'posts:profile_follow',
                args=(self.post.author.username,),
            ),
        )
        self.assertEqual(
            Follow.objects.filter(
                user=self.user[1],
                author=self.user[0],
            ).count(),
            1,
        )

    def test_new_post_visible_to_follower(self):
        self.auth.get(
            reverse(
                'posts:profile_follow',
                args=(self.post.author.username,),
            ),
        )
        self.assertContains(
            self.auth.get(reverse('posts:follow_index')),
            self.post.text,
        )

    def test_new_post_invisible_to_non_follower(self):
        self.assertNotContains(
            self.auth.get(reverse('posts:follow_index')),
            self.post.text,
        )

    def test_index_page_cache(self):
        response_one = self.client.get(reverse('posts:index'))
        response_one.context['page_obj'][0].delete()
        Post.objects.create(
            text='text',
            author=self.user[0],
            group=self.group[0],
        )
        response_two = self.client.get(reverse('posts:index'))
        self.assertEqual(response_one.content, response_two.content)
        cache.clear()
        response_three = self.client.get(reverse('posts:index'))
        self.assertNotEqual(
            response_two.content,
            response_three.content,
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.auth = Client()
        cls.auth.force_login(cls.user)

        cls.group = mixer.blend('posts.Group')

        cls.post = mixer.cycle(13).blend(
            'posts.Post',
            group=cls.group,
            author=cls.user,
        )

        cls.paginator_reverse_names = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': cls.user.username},
            ),
        )

    def setUp(self):
        cache.clear()

    def test_first_page_displays_propper_posts_number(self):
        for page in self.paginator_reverse_names:
            response = self.auth.get(page)
            self.assertEqual(
                len(response.context.get('page_obj')),
                settings.PAGE_SIZE,
            )
