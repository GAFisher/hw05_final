from http import HTTPStatus

from .base_testcase import PostTestCase


class PostURLTests(PostTestCase):
    def test_urls_exists_at_desired_location(self):
        """Страницы доступны любому пользователю."""
        url_names = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user}/',
            f'/posts/{self.post.id}/',
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_exists_at_desired_location_admin(self):
        """Страница доступна автору поста."""
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_authorized_client(self):
        """Страница доступна авторизованному пользователю."""
        url_names = ('/create/', '/follow/')
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirects_anonymous_on_admin_login(self):
        """Страница перенаправит анонимного пользователя
        на страницу логина."""
        create_url = '/auth/login/?next=/create/'
        posts_edit_url = f'/auth/login/?next=/posts/{self.post.id}/edit/'
        add_comment_url = f'/auth/login/?next=/posts/{self.post.id}/comment/'
        follow_url = '/auth/login/?next=/follow/'
        url_names = {
            '/create/': create_url,
            f'/posts/{self.post.id}/edit/': posts_edit_url,
            f'/posts/{self.post.id}/comment/': add_comment_url,
            '/follow/': follow_url,
        }
        for url, redirect in url_names.items():
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Проверяем, что несуществующая страница вернет ошибку 404."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
