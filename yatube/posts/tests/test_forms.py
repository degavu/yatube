import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.models import Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='group_test',
            slug='test_slug',
            description='Тестовое описание группы'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def tearDown(self):
        self.uploaded.close()

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(PostFormTests.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_create_post_form(self):

        form_data = {
            'text': 'Простая запись для поста',
            'group': PostFormTests.group.id,
            'image': self.uploaded
        }
        response = self.auth_client.post(reverse('posts:post_create'),
                                         data=form_data,
                                         follow=True)
        post = Post.objects.get(author=PostFormTests.user)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(
            post.image.name,
            Post.image.field.upload_to + form_data['image'].name
        )
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(post.author, PostFormTests.user)
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': PostFormTests.user})
        )

    def test_edit_post_form(self):
        TEST_POST_TEXT = 'Тестовый пост'
        Post.objects.create(
            author=PostFormTests.user,
            text=TEST_POST_TEXT,
            group=PostFormTests.group,
        )
        response = self.auth_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': '1'}))
        old_text = response.context['form']['text'].value()
        old_group = response.context['form']['group'].value()
        form_data = {
            'text': old_text * 2,
            'group': old_group,
        }
        response = self.auth_client.post(reverse(
            'posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True)
        post = Post.objects.get(id=1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(post.author, PostFormTests.user)

    def test_create_comment_form(self):
        """после успешной отправки комментарий появляется на странице поста"""
        TEST_POST_TEXT = 'Тестовый пост'
        TEST_COMMENT_TEXT = 'Тестовый комментарий'
        form_data = {
            'text': TEST_COMMENT_TEXT,
        }
        post = Post.objects.create(
            author=PostFormTests.user,
            text=TEST_POST_TEXT,
        )
        response = self.auth_client.post(reverse('posts:add_comment',
                                         kwargs={'post_id': post.id}),
                                         data=form_data,
                                         follow=True)
        self.assertEqual(response.context['comments'][0].text,
                         form_data['text'])
