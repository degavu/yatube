from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='user_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание бла-бла-бла',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='simple_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / (index) доступна любому пользователю."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_slug_url_exists_at_desired_location(self):
        """Страница /group/test_slug доступна любому пользователю."""
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': PostURLTests.group.slug})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_user_url_exists_at_desired_location(self):
        """Страница /profile/auth доступна любому пользователю."""
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': PostURLTests.user})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_url_exists_at_desired_location(self):
        """Страница /posts/id доступна любому пользователю."""
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostURLTests.post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_desired_location(self):
        """Страница /post_create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница /posts/id/edit/ доступна автору поста."""
        author_client = Client()
        author_client.force_login(PostURLTests.user)
        response = author_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostURLTests.post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_comment_add_url_non_exist_for_guest(self):
        """Добавление комментария для гостя недоступно"""
        response = self.guest_client.get(reverse(
            'posts:add_comment',
            kwargs={'post_id': PostURLTests.post.id})
        )
        self.assertTrue(reverse('users:login') in response.url)

    def test_non_expected_post(self):
        """Проверяем ответ 404, при попытке доступа к не существующему посту"""
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'non_exists_slug'})
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': PostURLTests.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': PostURLTests.user}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': PostURLTests.post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={
                'post_id': PostURLTests.post.id}): 'posts/create_post.html',
            'non_exist_page': 'core/404.html',
        }
        cache.clear()
        author_client = Client()
        author_client.force_login(PostURLTests.user)
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = author_client.get(address)
                self.assertTemplateUsed(response, template)
