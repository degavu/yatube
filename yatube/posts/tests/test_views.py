import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

from django.test import TestCase, Client, override_settings

from django.urls import reverse
from django import forms

from posts.models import Post, Group, User, Comment, Follow


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание бла-бла-бла',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded
        )
        cls.input_comment = Comment._meta.get_field('text').verbose_name

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def context_test_in_paginator(self, test_object):
        self.assertEqual(test_object.text, PostURLTests.post.text)
        self.assertEqual(test_object.author, PostURLTests.post.author)
        self.assertEqual(test_object.group, PostURLTests.post.group)
        self.assertEqual(test_object.image, PostURLTests.post.image)

    def test_following_auth_user(self):
        """Тест проверки работы системы подписки/отписки"""
        follower_user = User.objects.create_user(username='user_follower')
        follower_client = Client()
        follower_client.force_login(follower_user)
        # подписка
        response = follower_client.get(reverse(
            'posts:profile_follow', kwargs={'username': PostURLTests.user}))
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': PostURLTests.user}))
        follower = Follow.objects.all()
        self.assertEqual(1, len(follower))
        # отписка
        response = follower_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': PostURLTests.user}))
        self.assertRedirects(response, reverse('posts:follow_index'))
        follower = Follow.objects.all()
        self.assertEqual(0, len(follower))

    def test_new_post_in_followers(self):
        """тест появления запси у подписчика в ленте.
            Отсутсвтия записей в избранном у неподписчика
        """
        follower_user = User.objects.create_user(username='user_follower')
        any_user = User.objects.create_user(username='any_user')
        follower_client = Client()
        follower_client.force_login(follower_user)
        response = follower_client.get(reverse(
            'posts:profile_follow', kwargs={'username': PostURLTests.user}))
        response = follower_client.get(reverse('posts:follow_index'))
        test_context = response.context['page_obj'][0]
        self.assertEqual(test_context.text, PostURLTests.post.text)
        any_client = Client()
        any_client.force_login(any_user)
        response = any_client.get(reverse('posts:follow_index'))
        count_posts = len(response.context['page_obj'])
        self.assertEqual(count_posts, 0)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_url_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': PostURLTests.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': PostURLTests.user}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': PostURLTests.post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:post_edit', kwargs={
                'post_id': PostURLTests.post.id}): 'posts/create_post.html',
        }

        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.context_test_in_paginator(response.context['page_obj'][0])

    def test_group_list_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': PostURLTests.group.slug}))
        self.context_test_in_paginator(response.context['page_obj'][0])

    def test_profile_user_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': PostURLTests.user}))
        self.context_test_in_paginator(response.context['page_obj'][0])

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': PostURLTests.post.id}))
        test_object = response.context['post']
        self.assertEqual(test_object.text, PostURLTests.post.text)
        self.assertEqual(test_object.image, PostURLTests.post.image)
        self.assertEqual(test_object.author, PostURLTests.post.author)
        self.assertEqual(test_object.group, PostURLTests.post.group)

    def test_post_create_page_show_correct_context_form(self):
        """Шаблон create_post.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context_form(self):
        """Шаблон create_post.html (edit_post) cф-ан с прав-ым контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': PostURLTests.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_in_index_page(self):
        """Проверка работы кеша на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        old_content = response.content
        Post.objects.get(id=PostURLTests.post.id).delete()
        response = self.authorized_client.get(reverse('posts:index'))
        new_content = response.content
        self.assertEqual(old_content, new_content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        new_content = response.content
        self.assertNotEqual(old_content, new_content)


class PaginatorViewsTest(TestCase):
    templates_posts = [
        reverse('posts:index'),
        reverse('posts:group_list', kwargs={'slug': 'testslug'}),
        reverse('posts:profile', kwargs={'username': 'page_user'})
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='page_user')
        cls.group = Group.objects.create(
            title='PaginatorGroup',
            slug='testslug',
            description='Тестовое описание группы'
        )
        Post.objects.bulk_create([Post(
            text=f'Тестовый пост №{i}',
            author=cls.user,
            group=cls.group) for i in range(1, 16)]
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_first_page_contains_ten_records(self):
        cache.clear()
        for page in self.templates_posts:
            response = self.client.get(page)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        cache.clear()
        for page in self.templates_posts:
            response = self.client.get(page + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 5)
