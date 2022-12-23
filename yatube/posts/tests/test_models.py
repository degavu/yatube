from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей (post) корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у моделей (group) корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
