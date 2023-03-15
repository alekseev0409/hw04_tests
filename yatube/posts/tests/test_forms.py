from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from ..forms import PostForm
from ..models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.auth_user = User.objects.create_user(username='TestAuthUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст поста',
            group=cls.group,

        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(PostCreateFormTests.auth_user)
        self.authorized_client_author.force_login(PostCreateFormTests.author)

    def test_create_task(self):
        """Валидная форма создает запись в Posts."""
        post_count = Post.objects.count()

        form_data = {
            'text': 'Введенный в форму текст',
            'group': self.group.pk,
        }

        self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )

        new_post = Post.objects.latest('pub_date')
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.pk, form_data['group'])

    def test_author_edit_post(self):
        """Валидная форма изменяет запись в Posts."""
        form_data = {
            'text': 'Введенный в форму текст',
            'group': self.group.pk,
        }

        self.authorized_client_author.get(f'/posts/{self.post.pk}/edit/')
        form_data = {
            'text': 'Отредактированный в форме текст',
            'group': self.group.pk,
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )

        edit_post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.group.pk, form_data['group'])

    def test_create_new_post(self):
        "Отправка формы со страницы create"
        count = Post.objects.count()
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
            content_type='image/gif',
        )
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True,
        )
        new_post = Post.objects.latest('pub_date')
        self.assertEqual(Post.objects.count(), count + 1)
        self.assertEqual(new_post.text, self.post.text)
        self.assertEqual(new_post.group, self.post.group)
        self.assertTrue(new_post.image)
