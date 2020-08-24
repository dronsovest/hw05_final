from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache

from .models import Post, Group


User = get_user_model()

def test_context(self, response):
    self.assertEqual(response.context['page'][0].text, 'No fate')
    self.assertEqual(response.context['page'][0].author, self.user)
    self.assertEqual(response.context['page'][0].group, self.group)


class TestProfile(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sarah', email='s.conor@mail.ru', password='234567Abc'
        )
        self.group = Group.objects.create(
                                            title='test_group',
                                            slug='test_group',
                                            description='test'
                                         )
        self.client.force_login(self.user)
        self.post = self.client.post(reverse('new_post'), {
                                                            'text': 'No fate',
                                                            'group': 1
                                                          })

    def test_profile(self):
        response = self.client.get(reverse(
                                            'profile',
                                            args=[self.user.username]
                                          ))
        self.assertEqual(response.status_code, 200)

# Авторизованный пользователь может опубликовать пост (new)
    def test_new_post(self):
        self.assertEqual(Post.objects.all().count(), 1)
        first_post = Post.objects.first()
        self.assertEqual(first_post.text, 'No fate')
        self.assertEqual(first_post.author, self.user)
        self.assertEqual(first_post.group, self.group)

# После публикации поста новая запись появляется на главной странице сайта
    def test_post_index(self):
        response = self.client.get(reverse('index'))
        test_context(self, response)

# на персональной странице пользователя (profile)
    def test_post_profile(self):
        response = self.client.get(reverse(
                                            'profile',
                                            args=[self.user.username]
                                          ))
        test_context(self, response)

# и на отдельной странице поста (post)
    def test_post_page(self):
        response = self.client.get(reverse(
                                            'post',
                                            args=[
                                                    self.user.username,
                                                    Post.objects.first().id
                                                 ]
                                          ))
        self.assertEqual(response.context['post'].text, 'No fate')
        self.assertEqual(response.context['post'].author, self.user)
        self.assertEqual(response.context['post'].group, self.group)

# Авторизованный пользователь может отредактировать свой пост
# и его содержимое изменится на всех связанных страницах
    def test_post_edit(self):
        self.client.force_login(self.user)
        new_post = self.client.post(reverse(
                                            'post_edit',
                                            args=[
                                                    self.user.username,
                                                    Post.objects.first().id
                                                 ]
                                            ),
                                    {'text': 'T1000 - loh'}
                                    )
        response = self.client.get(reverse(
                                            'profile',
                                            args=[self.user.username]
                                          ))
        self.assertEqual(response.context['posts'][0].text, 'T1000 - loh')
        response = self.client.get(reverse(
                                            'profile',
                                            args=[self.user.username]
                                          ))
        self.assertEqual(response.context['posts'][0].group, None)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['page'][0].text, 'T1000 - loh')
        response = self.client.get(reverse(
                                            'post',
                                            args=[
                                                    self.user.username,
                                                    Post.objects.first().id
                                                 ]
                                          ))
        self.assertEqual(response.context['post'].text, 'T1000 - loh')

    def test_cache_index_page(self):
        self.client.force_login(self.user)
        self.post = self.client.post(reverse('new_post'), {
                                                            'text': 'test2',
                                                            'group': 1
                                                          })
        cache.clear()
        response = self.client.get(reverse('index'))
        self.assertIn('test2', response.content.decode())
        self.post = self.client.post(reverse('new_post'), {
                                                            'text': 'test3',
                                                            'group': 1
                                                          })
        response = self.client.get(reverse('index'))
        self.assertNotIn('test3', response.content.decode())
        cache.clear()
        response = self.client.get(reverse('index'))
        self.assertIn('test3', response.content.decode())

# Неавторизованный посетитель не может опубликовать пост
# (его редиректит на страницу входа)
    def test_post(self):
        self.client.logout()
        response = self.client.post(
                                    reverse('new_post'),
                                    {
                                        'text': 'Astala vista',
                                        'group': 1
                                    },
                                    follow=True
                                    )
        self.assertEqual(
                            response.redirect_chain,
                            [('/accounts/login/?next=/new/', 302)]
                        )
        self.assertEqual(Post.objects.all().count(), 1)

    def test_404(self):
        response = self.client.get(reverse(
                                            'post',
                                            args=[
                                                    'nouser',
                                                    99999
                                                 ]
                                          ))
        self.assertEqual(response.status_code, 404)


class TestImages(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah",
            email='s.conor@mail.ru',
            password='234567Abc'
        )
        self.client.force_login(self.user)
        self.group = Group.objects.create(title='testgroup', slug='testgroup')
        self.post = Post.objects.create(
            text='Test post',
            author=self.user,
            group=self.group)

    def test_images(self):
        with open('media/posts/Тест.jpg', 'rb') as img:
            response = self.client.post(reverse(
                                            'post_edit',
                                            args=[
                                                    self.user.username,
                                                    Post.objects.first().id
                                                 ]
                                            ),
                                    {'text': 'Test post with img', 'image':img},
                                    follow=True
                                    )
            self.assertIn('<img', str(response.content.decode()))

        response = self.client.get('')
        self.assertIn('<img', str(response.content.decode()))

        with open('media/posts/Тест.txt', 'rb') as img:
            response = self.client.post(reverse(
                                            'post_edit',
                                            args=[
                                                    self.user.username,
                                                    Post.objects.first().id
                                                 ]
                                        ),
                                    {'text': 'Test post with img', 'image':img},
                                    follow=True
                                    )
            errors = 'Отправленный файл пуст.'
            self.assertFormError(response, 'form', 'image', errors)
