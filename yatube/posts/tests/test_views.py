from django.conf import settings
from django.core.cache import cache
from django.urls import reverse

from .base_testcase import PostTestCase, Post, Group, User, TestCase
from ..forms import PostForm
from ..models import Follow


class PostPagesTests(PostTestCase):
    def test_pages_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author},
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.image, 'posts/small.gif')

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['group']
        self.assertEqual(first_object.title, self.group.title)
        self.assertEqual(first_object.slug, self.group.slug)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(response.context['author'], self.user)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post').text, 'Тестовый пост')
        self.assertEqual(response.context.get('post').author, self.user)
        self.assertEqual(response.context.get('post').group, self.group)
        self.assertEqual(response.context.get('post').image, 'posts/small.gif')

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон create_post(edit) сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertTrue(response.context['is_edit'])

    def test_post_create_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertFalse(response.context['is_edit'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = [
            Post(
                text='Тестовый пост',
                author=cls.user,
                group=cls.group,
            )
            for i in range(settings.POSTS_COUNT + settings.POSTS_COUNT // 3)
        ]
        Post.objects.bulk_create(cls.posts)
        cls.posts = Post.objects.all()

    def test_page_contains_records(self):
        pages = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            ),
            reverse('posts:profile', kwargs={'username': self.user}),
        )
        for reverse_name in pages:
            with self.subTest(reverse_name=reverse_name):
                response1 = self.client.get(reverse_name)
                response2 = self.client.get((reverse_name + '?page=2'))
                self.assertEqual(
                    len(response1.context['page_obj']), settings.POSTS_COUNT
                )
                self.assertEqual(
                    len(response2.context['page_obj']),
                    settings.POSTS_COUNT // 3,
                )


class CreatedViewsTest(PostTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_user = User.objects.create_user(username='new_author')
        cls.new_group = Group.objects.create(
            title='Новая тестовая группа',
            slug='new-test-slug',
            description='Тестовое описание новой группы',
        )
        cls.new_post = Post.objects.create(
            text='Новый тестовый пост',
            author=cls.new_user,
            group=cls.new_group,
        )

    def test_post_created_correct(self):
        """Пост попадает на главную страницу, в свою группу и профиль автора"""
        pages = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.new_group.slug},
            ),
            reverse('posts:profile', kwargs={'username': self.new_user}),
        )
        for reverse_name in pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                self.assertEqual(first_object.text, 'Новый тестовый пост')
                self.assertEqual(first_object.author, self.new_user)
                self.assertEqual(first_object.group, self.new_group)

    def test_post(self):
        """Пост не попал в группу, для которой не был предназначен."""
        posts_count = Post.objects.filter(group=self.group).count()
        self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            )
        )
        self.assertEqual(posts_count, 1)


class CacheTests(PostTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Тестовый пост для тестирования кэширования',
            author=cls.user,
            group=cls.group,
        )

    def test_cache_index_page(self):
        """Тест кэширования страницы index.html"""
        response_1 = self.client.get(reverse('posts:index'))
        post = Post.objects.first()
        post.delete()
        response_2 = self.client.get(reverse('posts:index'))
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response_1.content, response_3.content)


class FollowTests(PostTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Тестовый пост для тестирования новой записи',
            author=cls.user,
            group=cls.group,
        )

    def test_profile_follow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей.
        """
        follow_count = Follow.objects.count()
        self.authorized_follower.get(
            reverse('posts:profile_follow', kwargs={'username': self.user})
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_profile_unfollow(self):
        """Авторизованный пользователь может удалять
        других пользователей из подписок.
        """
        Follow.objects.create(user=self.follower, author=self.user)
        follow_count = Follow.objects.count()
        self.authorized_follower.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.user})
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_follow_created_correct(self):
        """Новая запись пользователя появляется в ленте подписчиков."""
        Follow.objects.create(user=self.follower, author=self.user)
        response = self.authorized_follower.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, self.post)
